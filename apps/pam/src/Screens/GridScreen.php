<?php

declare(strict_types=1);

namespace App\Screens;

use App\Support\Bench;
use App\Support\Page;
use Pam\Native\Component;
use Pam\Native\Element;
use Pam\Native\Style;
use Pam\Native\UI\Image;
use Pam\Native\UI\View;
use Pam\Native\UI\VirtualGrid;

/** 3-column grid of 500 remote images (default memory + disk cache). */
final class GridScreen extends Component
{
    private const int COUNT = 500;

    public function render(): Element
    {
        // Data-driven grid (PAM Native 1.45+).
        if (method_exists(VirtualGrid::class, 'of')) {
            return Page::make(
                VirtualGrid::of(3, range(0, self::COUNT - 1), fn (int $i): Element => $this->cell($i))
                    ->style(new Style(flexGrow: 1)),
            );
        }
        $cells = [];
        for ($i = 0; $i < self::COUNT; $i++) {
            $cells[] = View::make(
                Image::make(Bench::ASSETS."/img/{$i}.jpg")
                    ->onLoad($this->loaded(...))
                    ->style(new Style(widthPercent: 100, heightPercent: 100)),
            )->key((string) $i)->style(new Style(aspectRatio: 1, padding: 1));
        }

        return Page::make(
            VirtualGrid::make(3, ...$cells)->style(new Style(flexGrow: 1)),
        );
    }

    private function cell(int $i): Element
    {
        return View::make(
            Image::make(Bench::ASSETS."/img/{$i}.jpg")
                ->onLoad($this->loaded(...))
                ->style(new Style(widthPercent: 100, heightPercent: 100)),
        )->style(new Style(aspectRatio: 1, padding: 1));
    }

    /** First image decoded on screen (the closest native signal to "first frame with an image"). */
    public function loaded(): void
    {
        Bench::logOnce('grid', 'ready', scenario: 'grid');
    }
}
