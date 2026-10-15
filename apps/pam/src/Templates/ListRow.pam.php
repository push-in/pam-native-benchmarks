<?php

declare(strict_types=1);

namespace App\Templates;

use App\Support\Bench;
use App\Support\Lcg;
use Pam\Native\Component;

/** One row of the list scenario: compact, avatar or card (i % 3). */
final class ListRow extends Component
{
    public function __construct(public int $i = 0)
    {
    }

    public function avatarColor(): string
    {
        return sprintf('#%06X', Bench::PALETTE[$this->i % 8] & 0xFFFFFF);
    }

    public function cardText(): string
    {
        $lcg = new Lcg(42 + $this->i);
        $sentences = [];
        for ($k = ($this->i % 4) + 1; $k > 0; $k--) {
            $words = [];
            for ($w = 0; $w < 8; $w++) {
                $words[] = $lcg->word();
            }
            $sentences[] = ucfirst(implode(' ', $words)).'.';
        }

        return implode(' ', $sentences);
    }
}
?>

<template>
    <Column p-if="$i % 3 === 0" class="compact">
        <Text class="title">Item {{ $i }}</Text>
        <Text class="subtitle">Subtitle for item {{ $i }}</Text>
    </Column>
    <Row p-else-if="$i % 3 === 1" class="avatar-row">
        <View class="avatar" :backgroundColor="avatarColor()">
            <Text class="avatar-label">I{{ $i % 10 }}</Text>
        </View>
        <Column class="avatar-body">
            <Text class="title">Item {{ $i }}</Text>
            <Text class="subtitle">Subtitle for item {{ $i }}</Text>
        </Column>
        <Text class="badge">{{ $i % 100 }}</Text>
    </Row>
    <Column p-else class="card">
        <Text class="title">Card {{ $i }}</Text>
        <Text class="body">{{ cardText() }}</Text>
    </Column>
</template>

<style scoped>
    .compact { height: 64px; padding: 0 16px; justify-content: center; }
    .title { color: #111827; font-size: 16px; font-weight: 700; }
    .subtitle { color: #6B7280; font-size: 13px; }
    .avatar-row { height: 72px; padding: 0 16px; gap: 12px; align-items: center; }
    .avatar { width: 48px; height: 48px; border-radius: 24px; align-items: center; justify-content: center; }
    .avatar-label { color: #FFFFFF; font-size: 16px; font-weight: 700; }
    .avatar-body { flex-grow: 1; flex-shrink: 1; }
    .badge { padding: 2px 10px; background-color: #EEF2FF; color: #111827; font-size: 13px; border-radius: 999px; }
    .card { padding: 16px; gap: 4px; margin: 8px 16px; border-radius: 12px; background-color: #F3F4F6; }
    .body { color: #111827; font-size: 14px; }
</style>
