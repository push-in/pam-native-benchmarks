<?php

declare(strict_types=1);

namespace App\Support;

use Pam\Native\Style;

/**
 * Shared constants of suite/SCENARIOS.md and the BENCH event log.
 */
final class Bench
{
    public const string ASSETS = 'https://127.0.0.1:8099';

    public const int BACKGROUND = 0xFFFFFFFF;
    public const int TEXT = 0xFF111827;
    public const int MUTED = 0xFF6B7280;

    /** @var list<int> */
    public const array PALETTE = [
        0xFFEF4444, 0xFFF97316, 0xFFEAB308, 0xFF22C55E,
        0xFF06B6D4, 0xFF3B82F6, 0xFF8B5CF6, 0xFFEC4899,
    ];

    /** suite/words.txt */
    public const array WORDS = [
        'alpha', 'bravo', 'charlie', 'delta', 'echo', 'foxtrot', 'golf', 'hotel',
        'india', 'juliet', 'kilo', 'lima', 'mike', 'november', 'oscar', 'papa',
        'quebec', 'romeo', 'sierra', 'tango', 'uniform', 'victor', 'whiskey', 'xray',
        'yankee', 'zulu', 'amber', 'birch', 'cedar', 'dune', 'ember', 'fjord',
        'glacier', 'harbor', 'island', 'jungle', 'kettle', 'lantern', 'meadow', 'nectar',
        'orchard', 'pepper', 'quartz', 'river', 'saffron', 'timber', 'umbra', 'velvet',
        'willow', 'xenon', 'yarrow', 'zephyr', 'anchor', 'beacon', 'canyon', 'delta2',
        'ember2', 'falcon', 'garnet', 'hollow', 'ivory', 'jasper', 'kernel', 'lotus',
    ];

    /** @var array<string, true> */
    private static array $logged = [];

    private function __construct()
    {
    }

    /**
     * One `<event> key=value ...` line. The PAM host routes PHP error_log()
     * to logcat (tag `PamPHP`, priority INFO); there is no tagged log API.
     */
    public static function log(string $event, string|int|float ...$fields): void
    {
        $line = $event;
        foreach ($fields as $key => $value) {
            $line .= " {$key}={$value}";
        }
        error_log($line);
    }

    /** Logs an event line only the first time `$once` is seen in this process. */
    public static function logOnce(string $once, string $event, string|int|float ...$fields): void
    {
        if (isset(self::$logged[$once])) {
            return;
        }
        self::$logged[$once] = true;
        self::log($event, ...$fields);
    }

    public static function text(float $size, int $color = self::TEXT, ?int $weight = null): Style
    {
        return new Style(textColor: $color, fontSize: $size, fontWeight: $weight);
    }
}
