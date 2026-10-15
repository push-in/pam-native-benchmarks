package dev.bench.nativeapp

import android.content.Intent
import android.graphics.Color
import android.os.Bundle
import androidx.activity.SystemBarStyle
import androidx.activity.enableEdgeToEdge
import androidx.core.view.ViewCompat
import androidx.core.view.WindowInsetsCompat
import androidx.fragment.app.Fragment
import androidx.fragment.app.FragmentActivity
import androidx.fragment.app.commit

class MainActivity : FragmentActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        enableEdgeToEdge(
            statusBarStyle = SystemBarStyle.light(Color.TRANSPARENT, Color.TRANSPARENT),
            navigationBarStyle = SystemBarStyle.light(Color.TRANSPARENT, Color.TRANSPARENT),
        )
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val container = findViewById<android.view.View>(R.id.container)
        ViewCompat.setOnApplyWindowInsetsListener(container) { v, insets ->
            val bars = insets.getInsets(
                WindowInsetsCompat.Type.systemBars() or WindowInsetsCompat.Type.displayCutout(),
            )
            val ime = insets.getInsets(WindowInsetsCompat.Type.ime())
            v.setPadding(bars.left, bars.top, bars.right, maxOf(bars.bottom, ime.bottom))
            WindowInsetsCompat.CONSUMED
        }

        if (savedInstanceState == null) show(intent)
    }

    override fun onNewIntent(intent: Intent) {
        super.onNewIntent(intent)
        setIntent(intent)
        supportFragmentManager.popBackStackImmediate(null, androidx.fragment.app.FragmentManager.POP_BACK_STACK_INCLUSIVE)
        show(intent)
    }

    private fun show(intent: Intent?) {
        val uri = intent?.data
        val scenario = uri?.host ?: "home"
        val fragment: Fragment = when (scenario) {
            "list" -> ListFragment()
            "grid" -> GridFragment()
            "like" -> LikeFragment()
            "filter" -> FilterFragment()
            "anim" -> AnimFragment()
            "nav" -> NavFragment.newInstance(0)
            "video" -> VideoFragment()
            "feed" -> FeedFragment()
            "compute" -> ComputeFragment()
            "state" -> StateFragment.newInstance(uri?.getQueryParameter("n")?.toIntOrNull() ?: 0)
            else -> HomeFragment()
        }
        supportFragmentManager.commit {
            setReorderingAllowed(true)
            replace(R.id.container, fragment)
        }
    }
}
