import { useEffect, useRef, useState } from 'react'
import WaveSurfer from 'wavesurfer.js'
import Spectrogram from 'wavesurfer.js/dist/plugins/spectrogram.esm.js'
import RegionsPlugin from 'wavesurfer.js/dist/plugins/regions.esm.js'
import type { Detection } from '../types'
import { magma } from '../lib/util'

// only one clip plays at a time across the whole page
let current: WaveSurfer | null = null

export function Player({ det }: { det: Detection }) {
  const elRef = useRef<HTMLDivElement>(null)
  const wsRef = useRef<WaveSurfer | null>(null)
  const stopAt = useRef<number | null>(null)
  const [ready, setReady] = useState(false)
  const [playing, setPlaying] = useState(false)
  const [info, setInfo] = useState('decoding clip…')

  useEffect(() => {
    if (!elRef.current) return
    const ws = WaveSurfer.create({
      container: elRef.current,
      height: 40,
      waveColor: '#3c5340',
      progressColor: '#9ccb5e',
      cursorColor: '#f06a4a',
      cursorWidth: 2,
      minPxPerSec: 100,
      autoScroll: true,
      autoCenter: true,
      dragToSeek: true,
      url: det.audio,
      sampleRate: 48000,
    })
    wsRef.current = ws
    const regions = ws.registerPlugin(RegionsPlugin.create())
    ws.registerPlugin(
      Spectrogram.create({
        height: 168,
        labels: true,
        labelsColor: '#8aa18f',
        labelsBackground: 'rgba(11,17,13,0.6)',
        fftSamples: 512,
        frequencyMax: 12000,
        scale: 'linear',
        colorMap: magma() as unknown as number[][],
      })
    )

    ws.on('decode', () => {
      regions.addRegion({
        start: det.start, end: det.end,
        color: 'rgba(240,106,74,0.16)', drag: false, resize: false,
      })
      ws.setTime(Math.max(0, det.start - 0.15))
      setReady(true)
      setInfo(`detection ${det.start.toFixed(1)}–${det.end.toFixed(1)} s · clip ${ws.getDuration().toFixed(0)} s`)
    })
    ws.on('timeupdate', (t) => {
      if (stopAt.current !== null && t >= stopAt.current) { ws.pause(); stopAt.current = null }
    })
    ws.on('play', () => { if (current && current !== ws) current.pause(); current = ws; setPlaying(true) })
    ws.on('pause', () => setPlaying(false))
    ws.on('finish', () => setPlaying(false))
    ws.on('error', () => setInfo('could not load audio (is the server running?)'))

    return () => { if (current === ws) current = null; ws.destroy() }
  }, [det.audio, det.start, det.end])

  const playDetection = () => {
    const ws = wsRef.current; if (!ws) return
    ws.setTime(Math.max(0, det.start - 0.15)); stopAt.current = det.end + 0.15; ws.play()
  }
  const toggleFull = () => {
    const ws = wsRef.current; if (!ws) return
    stopAt.current = null; ws.playPause()
  }

  return (
    <div className="border-t border-line bg-base/40">
      <div className="px-3 pt-3"><div ref={elRef} className={ready ? '' : 'opacity-40'} /></div>
      <div className="flex items-center gap-2 px-3 py-2.5">
        <button
          onClick={playDetection} disabled={!ready}
          className={`rounded-md bg-moss/90 px-3 py-1.5 text-[13px] font-semibold text-base transition hover:bg-moss-bright disabled:opacity-40 ${playing ? 'recording' : ''}`}
        >▶ Play detection</button>
        <button
          onClick={toggleFull} disabled={!ready}
          className="rounded-md border border-line-2 px-3 py-1.5 text-[13px] text-ink/90 transition hover:bg-panel-2 disabled:opacity-40"
        >{playing ? 'Pause' : 'Play full clip'}</button>
        <span className="ml-auto font-mono text-[11px] text-faint">{info}</span>
      </div>
    </div>
  )
}
