package dev.bench.nativeapp

import android.graphics.Rect
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ImageView
import androidx.fragment.app.Fragment
import androidx.recyclerview.widget.GridLayoutManager
import androidx.recyclerview.widget.RecyclerView
import coil3.load

class GridFragment : Fragment(R.layout.fragment_recycler) {
    private var readyLogged = false

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        val list = view as RecyclerView
        val gap = resources.getDimensionPixelSize(R.dimen.grid_gap)
        list.layoutManager = GridLayoutManager(requireContext(), COLUMNS)
        list.setHasFixedSize(true)
        list.addItemDecoration(GapDecoration(gap))
        list.adapter = GridAdapter { image -> onFirstImage(image) }
    }

    private fun onFirstImage(image: ImageView) {
        if (readyLogged) return
        readyLogged = true
        logReadyAfterDraw(image, "ready scenario=grid")
    }

    private class GapDecoration(private val gap: Int) : RecyclerView.ItemDecoration() {
        override fun getItemOffsets(out: Rect, view: View, parent: RecyclerView, state: RecyclerView.State) {
            val column = parent.getChildAdapterPosition(view) % COLUMNS
            // Distribute 2 gaps of `gap` px over 3 equal cells.
            out.left = column * gap / COLUMNS
            out.right = gap - (column + 1) * gap / COLUMNS
            out.bottom = gap
        }
    }

    private class GridAdapter(
        private val onLoaded: (ImageView) -> Unit,
    ) : RecyclerView.Adapter<GridAdapter.Holder>() {
        class Holder(val image: ImageView) : RecyclerView.ViewHolder(image)

        override fun getItemCount() = 500

        override fun onCreateViewHolder(parent: ViewGroup, viewType: Int) =
            Holder(LayoutInflater.from(parent.context).inflate(R.layout.item_grid, parent, false) as ImageView)

        override fun onBindViewHolder(holder: Holder, position: Int) {
            holder.image.load("${Bench.HOST}/img/$position.jpg") {
                listener(onSuccess = { _, _ -> onLoaded(holder.image) })
            }
        }
    }

    private companion object {
        const val COLUMNS = 3
    }
}
