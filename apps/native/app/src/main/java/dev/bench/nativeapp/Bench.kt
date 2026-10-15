package dev.bench.nativeapp

import android.content.Context
import android.util.Log
import android.view.View
import androidx.core.view.doOnPreDraw
import androidx.fragment.app.Fragment
import okhttp3.Cache
import okhttp3.OkHttpClient
import java.io.File

/** Shared constants and helpers mandated by suite/SCENARIOS.md. */
object Bench {
    const val TAG = "BENCH"
    const val HOST = "https://127.0.0.1:8099"

    val WORDS = arrayOf("alpha", "bravo", "charlie", "delta", "echo", "foxtrot", "golf", "hotel", "india", "juliet", "kilo", "lima", "mike", "november", "oscar", "papa", "quebec", "romeo", "sierra", "tango", "uniform", "victor", "whiskey", "xray", "yankee", "zulu", "amber", "birch", "cedar", "dune", "ember", "fjord", "glacier", "harbor", "island", "jungle", "kettle", "lantern", "meadow", "nectar", "orchard", "pepper", "quartz", "river", "saffron", "timber", "umbra", "velvet", "willow", "xenon", "yarrow", "zephyr", "anchor", "beacon", "canyon", "delta2", "ember2", "falcon", "garnet", "hollow", "ivory", "jasper", "kernel", "lotus")

    val PALETTE = intArrayOf(
        0xFFEF4444.toInt(), 0xFFF97316.toInt(), 0xFFEAB308.toInt(), 0xFF22C55E.toInt(),
        0xFF06B6D4.toInt(), 0xFF3B82F6.toInt(), 0xFF8B5CF6.toInt(), 0xFFEC4899.toInt(),
    )

    fun log(message: String) {
        Log.i(TAG, message)
    }

    @Volatile
    private var client: OkHttpClient? = null

    /** One OkHttp client with a 10 MB disk cache for app data requests. */
    fun http(context: Context): OkHttpClient = client ?: synchronized(this) {
        client ?: OkHttpClient.Builder()
            .cache(Cache(File(context.applicationContext.cacheDir, "http"), 10L * 1024 * 1024))
            .build()
            .also { client = it }
    }
}

/** LCG from the contract: x = (x * 1103515245 + 12345) mod 2^31. */
class Lcg(seed: Long) {
    private var x = seed

    fun next(): Long {
        x = (x * 1103515245L + 12345L) and 0x7FFFFFFFL
        return x
    }

    fun word(): String = Bench.WORDS[(next() % 64).toInt()]
}

/** Logs `ready ...` after the first frame that draws [view]'s current content. */
fun Fragment.logReadyAfterDraw(view: View, message: String) {
    view.doOnPreDraw {
        view.post {
            Bench.log(message)
            activity?.reportFullyDrawn()
        }
    }
}
