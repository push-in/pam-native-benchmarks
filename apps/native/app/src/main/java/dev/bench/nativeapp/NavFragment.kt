package dev.bench.nativeapp

import android.os.Bundle
import android.util.TypedValue
import android.view.View
import android.widget.ImageView
import android.widget.LinearLayout
import android.widget.TextView
import androidx.core.content.ContextCompat
import androidx.fragment.app.Fragment
import androidx.fragment.app.commit
import coil3.load

class NavFragment : Fragment(R.layout.fragment_nav) {
    private val k: Int get() = requireArguments().getInt(ARG_K)

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        val k = k
        view.findViewById<TextView>(R.id.title).text = "Screen $k"
        view.findViewById<ImageView>(R.id.image).load("${Bench.HOST}/img/$k.jpg")
        view.findViewById<View>(R.id.next).setOnClickListener {
            parentFragmentManager.commit {
                setReorderingAllowed(true)
                replace(R.id.container, newInstance(k + 1))
                addToBackStack("screen-${k + 1}")
            }
        }
        val content = view.findViewById<LinearLayout>(R.id.content)
        val rowHeight = TypedValue.applyDimension(TypedValue.COMPLEX_UNIT_DIP, 40f, resources.displayMetrics).toInt()
        val textColor = ContextCompat.getColor(requireContext(), R.color.text)
        repeat(ROWS) { j ->
            content.addView(
                TextView(requireContext()).apply {
                    text = "Row $j"
                    textSize = 16f
                    setTextColor(textColor)
                    gravity = android.view.Gravity.CENTER_VERTICAL
                },
                LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, rowHeight),
            )
        }
        logReadyAfterDraw(view, "ready scenario=nav k=$k")
    }

    companion object {
        private const val ARG_K = "k"
        private const val ROWS = 50

        fun newInstance(k: Int) = NavFragment().apply {
            arguments = Bundle().apply { putInt(ARG_K, k) }
        }
    }
}
