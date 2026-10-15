<?php

declare(strict_types=1);

namespace App\Screens;

use App\Support\Bench;
use App\Support\Page;
use Pam\Native\Component;
use Pam\Native\Element;
use Pam\Native\Style;
use Pam\Native\UI\MediaPlayer;

/** One muted, looping, autoplaying 16:9 player without controls. */
final class VideoScreen extends Component
{
    public function render(): Element
    {
        return Page::make(
            MediaPlayer::make(Bench::ASSETS.'/video.mp4')
                ->autoPlay()
                ->loop()
                ->muted()
                ->controls(false)
                ->onReady(static fn () => Bench::logOnce('video', 'ready', scenario: 'video'))
                ->style(new Style(widthPercent: 100, aspectRatio: 16 / 9)),
        );
    }
}
