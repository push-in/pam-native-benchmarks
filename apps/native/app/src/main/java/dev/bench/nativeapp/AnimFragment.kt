package dev.bench.nativeapp

import android.animation.ObjectAnimator
import android.animation.ValueAnimator
import android.os.Bundle
import android.view.View
import android.view.animation.AccelerateDecelerateInterpolator
import android.view.animation.LinearInterpolator
import androidx.fragment.app.Fragment

class AnimFragment : Fragment(R.layout.fragment_anim) {
    private var rotate: ObjectAnimator? = null
    private var move: ObjectAnimator? = null

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        val square = view.findViewById<View>(R.id.square)
        val distance = 150f * resources.displayMetrics.density
        rotate = ObjectAnimator.ofFloat(square, View.ROTATION, 0f, 360f).apply {
            duration = 1000
            interpolator = LinearInterpolator()
            repeatCount = ValueAnimator.INFINITE
            repeatMode = ValueAnimator.RESTART
        }
        // 0 -> 150dp in 1000 ms, reversed back in 1000 ms: 2000 ms ease-in-out cycle.
        move = ObjectAnimator.ofFloat(square, View.TRANSLATION_X, 0f, distance).apply {
            duration = 1000
            interpolator = AccelerateDecelerateInterpolator()
            repeatCount = ValueAnimator.INFINITE
            repeatMode = ValueAnimator.REVERSE
        }
        logReadyAfterDraw(view, "ready scenario=anim")
    }

    override fun onStart() {
        super.onStart()
        rotate?.let { if (it.isPaused) it.resume() else it.start() }
        move?.let { if (it.isPaused) it.resume() else it.start() }
    }

    override fun onStop() {
        rotate?.pause()
        move?.pause()
        super.onStop()
    }

    override fun onDestroyView() {
        rotate?.cancel()
        move?.cancel()
        rotate = null
        move = null
        super.onDestroyView()
    }
}
