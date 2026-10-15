<?php

declare(strict_types=1);

namespace App\Templates;

use App\Support\Bench;
use Pam\Native\Component;

/** 10,000 rows of three kinds (i % 3), written the common way: a template p-for. */
final class ListPage extends Component
{
    /** @var list<int> */
    public array $items = [];

    public function boot(): void
    {
        $this->items = range(0, 9_999);
    }

    public function attached(): void
    {
        Bench::log('ready', scenario: 'list');
    }
}
?>

<template>
    <Screen class="page">
        <SafeAreaView class="page">
            <Column class="grow">
                <VirtualizedList estimatedRowHeight="72" class="grow">
                    <ListRow p-for="$i in $items" :key="$i" :i="$i" />
                </VirtualizedList>
            </Column>
        </SafeAreaView>
    </Screen>
</template>

<style scoped>
    .page { flex-grow: 1; background-color: #FFFFFF; }
    .grow { flex-grow: 1; }
</style>
