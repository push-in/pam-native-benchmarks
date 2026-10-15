<?php

declare(strict_types=1);

namespace App\Templates;

use App\Support\Bench;
use Pam\Native\Component;

/** 3-column grid of 500 remote images, written as a template p-for. */
final class GridPage extends Component
{
    /** @var list<int> */
    public array $items = [];

    public string $assets = Bench::ASSETS;

    public function boot(): void
    {
        $this->items = range(0, 499);
    }

    /** First image decoded on screen. */
    public function loaded(): void
    {
        Bench::logOnce('grid', 'ready', scenario: 'grid');
    }
}
?>

<template>
    <Screen class="page">
        <SafeAreaView class="page">
            <Column class="grow">
                <VirtualGrid columns="3" class="grow">
                    <View p-for="$i in $items" :key="$i" class="cell">
                        <Image :source="$assets.'/img/'.$i.'.jpg'" class="fill" on:load="loaded" />
                    </View>
                </VirtualGrid>
            </Column>
        </SafeAreaView>
    </Screen>
</template>

<style scoped>
    .page { flex-grow: 1; background-color: #FFFFFF; }
    .grow { flex-grow: 1; }
    .cell { aspect-ratio: 1; padding: 1px; }
    .fill { width: 100%; height: 100%; }
</style>
