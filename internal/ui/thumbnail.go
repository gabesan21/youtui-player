package ui

import (
	"context"
	"crypto/md5"
	"fmt"
	"image"
	"image/jpeg"
	_ "image/png"
	"net/http"
	"os"
	"path/filepath"
	"time"

	"github.com/nfnt/resize"
)

type ThumbnailCache struct {
	cacheDir string
}

func NewThumbnailCache() (*ThumbnailCache, error) {
	var baseDir string
	if xdg := os.Getenv("XDG_CACHE_HOME"); xdg != "" {
		baseDir = xdg
	} else {
		homeDir, err := os.UserHomeDir()
		if err != nil {
			return nil, err
		}
		baseDir = filepath.Join(homeDir, ".cache")
	}

	cacheDir := filepath.Join(baseDir, "youtui-player", "thumbnails")
	if err := os.MkdirAll(cacheDir, 0o755); err != nil {
		return nil, err
	}

	return &ThumbnailCache{
		cacheDir: cacheDir,
	}, nil
}

func (tc *ThumbnailCache) hashURL(url string) string {
	h := md5.Sum([]byte(url))
	return fmt.Sprintf("%x", h)
}

func (tc *ThumbnailCache) getCachePath(url string) string {
	hash := tc.hashURL(url)
	return filepath.Join(tc.cacheDir, hash+".jpg")
}

func (tc *ThumbnailCache) downloadImageWithContext(ctx context.Context, url string) (image.Image, error) {
	client := &http.Client{
		Timeout: 5 * time.Second,
	}

	req, err := http.NewRequestWithContext(ctx, "GET", url, nil)
	if err != nil {
		return nil, fmt.Errorf("create request failed: %w", err)
	}

	resp, err := client.Do(req)
	if err != nil {
		return nil, fmt.Errorf("download failed: %w", err)
	}

	defer func() {
		_ = resp.Body.Close()
	}()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("http status: %d", resp.StatusCode)
	}

	img, _, err := image.Decode(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("decode failed: %w", err)
	}

	return img, nil
}

func (tc *ThumbnailCache) GetThumbnailImage(url string) (image.Image, error) {
	return tc.GetThumbnailImageWithContext(context.Background(), url)
}

func (tc *ThumbnailCache) GetThumbnailImageWithContext(ctx context.Context, url string) (image.Image, error) {
	if url == "" {
		return nil, fmt.Errorf("empty URL")
	}

	cachePath := tc.getCachePath(url)

	if _, statErr := os.Stat(cachePath); statErr == nil {
		f, err := os.Open(cachePath)
		if err == nil {

			defer func() {
				_ = f.Close()
			}()

			img, _, err := image.Decode(f)
			if err == nil {
				return img, nil
			}
		}
	}

	img, err := tc.downloadImageWithContext(ctx, url)
	if err != nil {
		return nil, err
	}

	if err := tc.saveImageToCache(img, cachePath); err != nil {
		fmt.Printf("error: %s", err)
	}

	return img, nil
}

// thumbnailMaxEdge caps the cached image edge. The old 100px cap was enough
// for the pixelated blocks sink but too coarse for Kitty image rendering;
// 640 keeps kitty sharp (it scales to the placement cells itself) while
// bounding disk use, and the blocks sink reads the same files unchanged.
const thumbnailMaxEdge = 640

func (tc *ThumbnailCache) saveImageToCache(img image.Image, cachePath string) error {
	f, err := os.Create(cachePath)
	if err != nil {
		return err
	}

	defer func() {
		_ = f.Close()
	}()

	resized := resize.Thumbnail(thumbnailMaxEdge, thumbnailMaxEdge, img, resize.Lanczos3)

	return jpeg.Encode(f, resized, &jpeg.Options{Quality: 90})
}

// GetThumbnailPath returns the on-disk cache file for a thumbnail, downloading
// and caching it first when needed. The Kitty sink transmits from this path.
func (tc *ThumbnailCache) GetThumbnailPath(url string) (string, error) {
	return tc.GetThumbnailPathWithContext(context.Background(), url)
}

func (tc *ThumbnailCache) GetThumbnailPathWithContext(ctx context.Context, url string) (string, error) {
	if url == "" {
		return "", fmt.Errorf("empty URL")
	}

	cachePath := tc.getCachePath(url)

	if _, err := os.Stat(cachePath); err == nil {
		return cachePath, nil
	}

	img, err := tc.downloadImageWithContext(ctx, url)
	if err != nil {
		return "", err
	}

	if err := tc.saveImageToCache(img, cachePath); err != nil {
		return "", err
	}

	return cachePath, nil
}

// fetchListThumbnail delivers a list item thumbnail through the active sink:
// the Kitty image path when kitty mode is on, the pixelated blocks image
// otherwise. Delivery is guarded by the item's current thumbnail URL so a
// fetch from a stale page/scroll position never paints over the new content.
func (a *SimpleApp) fetchListThumbnail(list *CustomList, index int, url string) {
	if a.thumbCache == nil {
		return
	}

	go func() {
		if a.kitty != nil {
			path, err := a.thumbCache.GetThumbnailPath(url)
			if err != nil {
				return
			}
			a.app.QueueUpdateDraw(func() {
				list.SetKittyThumbnail(index, url, path)
			})
			return
		}

		img, err := a.thumbCache.GetThumbnailImage(url)
		if err != nil || img == nil {
			return
		}
		a.app.QueueUpdateDraw(func() {
			list.SetThumbnail(index, url, img)
		})
	}()
}
