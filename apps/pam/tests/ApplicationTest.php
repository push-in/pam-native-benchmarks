<?php

declare(strict_types=1);

use PHPUnit\Framework\TestCase;

final class ApplicationTest extends TestCase
{
    public function testNativeApplicationManifestIsPresent(): void
    {
        self::assertFileExists(dirname(__DIR__).'/pam-native.json');
        self::assertFileExists(dirname(__DIR__).'/index.php');
    }
}
