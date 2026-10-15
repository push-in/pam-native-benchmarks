package dev.bench.nativeapp

import android.os.Bundle
import android.view.SurfaceView
import android.view.View
import androidx.fragment.app.Fragment
import androidx.media3.common.MediaItem
import androidx.media3.common.Player
import androidx.media3.exoplayer.ExoPlayer

class VideoFragment : Fragment(R.layout.fragment_video) {
    private var player: ExoPlayer? = null
    private var readyLogged = false

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        val surface = view.findViewById<SurfaceView>(R.id.surface)
        player = ExoPlayer.Builder(requireContext()).build().apply {
            setVideoSurfaceView(surface)
            volume = 0f
            repeatMode = Player.REPEAT_MODE_ONE
            setMediaItem(MediaItem.fromUri("${Bench.HOST}/video.mp4"))
            addListener(object : Player.Listener {
                override fun onRenderedFirstFrame() {
                    if (readyLogged) return
                    readyLogged = true
                    Bench.log("ready scenario=video")
                    activity?.reportFullyDrawn()
                }
            })
            playWhenReady = true
            prepare()
        }
    }

    override fun onStart() {
        super.onStart()
        player?.play()
    }

    override fun onStop() {
        player?.pause()
        super.onStop()
    }

    override fun onDestroyView() {
        player?.release()
        player = null
        super.onDestroyView()
    }
}
