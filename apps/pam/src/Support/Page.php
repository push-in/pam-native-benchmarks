<?php

declare(strict_types=1);

namespace App\Support;

use Pam\Native\Element;
use Pam\Native\Renderable;
use Pam\Native\Style;
use Pam\Native\UI\Column;
use Pam\Native\UI\SafeAreaView;
use Pam\Native\UI\Screen;

/** White screen whose content stays inside the status/navigation bar insets. */
final class Page
{
    private function __construct()
    {
    }

    public static function make(Renderable|false|null ...$children): Element
    {
        return Screen::make(
            SafeAreaView::make(
                Column::make(...$children)->style(new Style(flexGrow: 1)),
            )->style(new Style(flexGrow: 1, backgroundColor: Bench::BACKGROUND)),
        )->style(new Style(flexGrow: 1, backgroundColor: Bench::BACKGROUND));
    }
}
