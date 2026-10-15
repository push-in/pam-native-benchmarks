<?php

declare(strict_types=1);

use App\Screens\AnimScreen;
use App\Screens\ComputeScreen;
use App\Screens\FeedScreen;
use App\Screens\FilterScreen;
use App\Screens\GridScreen;
use App\Screens\HomeScreen;
use App\Screens\LikeScreen;
use App\Screens\ListScreen;
use App\Screens\NavScreen;
use App\Screens\StateScreen;
use App\Screens\VideoScreen;
use App\Templates\FilterPage;
use App\Templates\GridPage;
use App\Templates\LikePage;
use App\Templates\ListPage;
use Pam\Native\App;
use Pam\Native\Renderable;
use Pam\Native\Navigation\NavigationContainer;
use Pam\Native\Navigation\NavigationTransition;
use Pam\Native\Navigation\Navigator;
use Pam\Native\Navigation\RouteContext;
use Pam\Native\Routing\Route;

require __DIR__.'/vendor/autoload.php';

// VirtualizedList materializes every row in PHP: the first full frame of the
// 10,000-row `list` scenario peaks at ~126 MB, at PHP's 128M default.
ini_set('memory_limit', '256M');

App::components(__DIR__.'/src', __DIR__.'/.pam-native/components');

/** @var ?Navigator $navigator */
$navigator = null;

// bench://<scenario>?<params>: custom schemes match the URI host against the
// route deep links. Without a launch URI the app stays on `home`.
$navigator = Route::stack(
    name: 'bench',
    initial: 'home',
    routes: static function () use (&$navigator): void {
        Route::screen('home', static fn (): HomeScreen => new HomeScreen($navigator));
        // The list scenarios use templates with p-for (the common way to
        // write PAM screens); `?api=builder` opens the PHP builder version
        // (VirtualizedList::of on 1.45+) for the same scenario.
        $variant = static fn (string $template, string $builder): Closure => static fn (RouteContext $route): Renderable
            => $route->string('api', 'template') === 'builder' ? new $builder() : App::make($template);
        Route::screen('list', $variant(ListPage::class, ListScreen::class))->deepLink('/list');
        Route::screen('grid', $variant(GridPage::class, GridScreen::class))->deepLink('/grid');
        Route::screen('like', $variant(LikePage::class, LikeScreen::class))->deepLink('/like');
        Route::screen('filter', $variant(FilterPage::class, FilterScreen::class))->deepLink('/filter');
        Route::screen('anim', AnimScreen::class)->deepLink('/anim');
        Route::screen('nav', static fn (RouteContext $route): NavScreen => new NavScreen($route->integer('k', 0) ?? 0))
            ->deepLink('/nav');
        Route::screen('video', VideoScreen::class)->deepLink('/video');
        Route::screen('feed', FeedScreen::class)->deepLink('/feed');
        Route::screen('compute', ComputeScreen::class)->deepLink('/compute');
        Route::screen('state', static fn (RouteContext $route): StateScreen => new StateScreen(
            max(0, (int) ($route->string('n', '0') ?? '0')),
        ))->deepLink('/state');
    },
    transition: NavigationTransition::None,
    durationMs: 0,
    restoreState: false,
);

// Cold- and warm-start bench:// links are routed by the container.
App::run(NavigationContainer::make($navigator)->linking());
