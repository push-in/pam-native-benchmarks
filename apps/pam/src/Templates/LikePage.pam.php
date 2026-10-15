<?php

declare(strict_types=1);

namespace App\Templates;

use App\Support\Bench;
use Pam\Native\Component;

/** 200 rows with a like toggle, written as a template p-for. */
final class LikePage extends Component
{
    /** @var list<int> */
    public array $items = [];

    /** @var array<int, true> */
    public array $liked = [];

    public function boot(): void
    {
        $this->items = range(0, 199);
    }

    public function attached(): void
    {
        Bench::log('ready', scenario: 'like');
    }

    public function isLiked(int $i): bool
    {
        return isset($this->liked[$i]);
    }

    public function likeLabel(int $i): string
    {
        $likes = $i * 7 % 50;

        return isset($this->liked[$i]) ? '♥ '.($likes + 1) : "♡ {$likes}";
    }

    public function toggle(int $i): void
    {
        $liked = $this->liked;
        if (isset($liked[$i])) {
            unset($liked[$i]);
        } else {
            $liked[$i] = true;
        }
        $this->liked = $liked;
        Bench::log('like', i: $i, liked: isset($this->liked[$i]) ? 1 : 0);
    }
}
?>

<template>
    <Screen class="page">
        <SafeAreaView class="page">
            <Column class="grow">
                <VirtualizedList estimatedRowHeight="72" class="grow">
                    <Column p-for="$i in $items" :key="$i" :class="['like-row', 'liked' => isLiked($i)]">
                        <Text class="title">Post {{ $i }}</Text>
                        <TouchableWithoutFeedback
                            class="like-button"
                            :accessibilityLabel="'like-'.$i"
                            accessibilityRole="button"
                            on:press="toggle($i)"
                        >
                            <Text class="like-label">{{ likeLabel($i) }}</Text>
                        </TouchableWithoutFeedback>
                    </Column>
                </VirtualizedList>
            </Column>
        </SafeAreaView>
    </Screen>
</template>

<style scoped>
    .page { flex-grow: 1; background-color: #FFFFFF; }
    .grow { flex-grow: 1; }
    .like-row { height: 72px; padding: 0 16px; justify-content: center; background-color: #FFFFFF; }
    .liked { background-color: #FFE4E6; }
    .title { color: #111827; font-size: 16px; font-weight: 700; }
    .like-button { padding: 6px 0; align-self: flex-start; }
    .like-label { color: #111827; font-size: 15px; }
</style>
