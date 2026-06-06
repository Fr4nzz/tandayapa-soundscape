import WaveSurfer from './vendor/wavesurfer.esm.js'
import Spectrogram from './vendor/spectrogram.esm.js'
import Regions from './vendor/regions.esm.js'

const DATA = (window.GALLERY && window.GALLERY.detections) || []
const META = (window.GALLERY && window.GALLERY.meta) || { species: [], recorders: [], habitats: [] }
const PAGE_SIZE = 12
let activeWs = null   // currently-playing player (so only one plays at a time)

const state = { search: '', group: '', habitat: '', recorder: '', daynight: '', hourMin: 0, conf: 0.25, sort: 'conf-desc', page: 0 }

const $ = (id) => document.getElementById(id)
const fmt = (n) => n.toFixed(2)

function confColor(c) {
  if (c >= 0.9) return '#2C5F2D'
  if (c >= 0.75) return '#5a8a3a'
  if (c >= 0.6) return '#D9A441'
  return '#b0772a'
}

// ---- populate filter controls ----------------------------------------------
function initControls() {
  $('species-list').innerHTML = META.species.map(s => `<option value="${s}">`).join('')
  $('f-habitat').innerHTML += META.habitats.map(h => `<option value="${h}">${h}</option>`).join('')
  $('f-recorder').innerHTML += META.recorders.map(r => `<option value="${r}">${r}</option>`).join('')

  $('f-search').addEventListener('input', e => { state.search = e.target.value.toLowerCase(); state.page = 0; render() })
  $('f-group').addEventListener('change', e => { state.group = e.target.value; state.page = 0; render() })
  $('f-habitat').addEventListener('change', e => { state.habitat = e.target.value; state.page = 0; render() })
  $('f-recorder').addEventListener('change', e => { state.recorder = e.target.value; state.page = 0; render() })
  $('f-daynight').addEventListener('change', e => { state.daynight = e.target.value; state.page = 0; render() })
  $('f-hour-min').addEventListener('input', e => { state.hourMin = +e.target.value; $('hour-val').textContent = e.target.value; state.page = 0; render() })
  $('f-conf').addEventListener('input', e => { state.conf = +e.target.value; $('conf-val').textContent = fmt(+e.target.value); state.page = 0; render() })
  $('f-sort').addEventListener('change', e => { state.sort = e.target.value; render() })
  $('f-reset').addEventListener('click', () => {
    Object.assign(state, { search: '', group: '', habitat: '', recorder: '', daynight: '', hourMin: 0, conf: 0.25, sort: 'conf-desc', page: 0 })
    $('f-search').value = ''; $('f-group').value = ''; $('f-habitat').value = ''; $('f-recorder').value = ''
    $('f-daynight').value = ''; $('f-hour-min').value = 0; $('hour-val').textContent = '0'
    $('f-conf').value = 0.25; $('conf-val').textContent = '0.25'; $('f-sort').value = 'conf-desc'
    render()
  })
}

// ---- filtering + sorting ---------------------------------------------------
function filtered() {
  let out = DATA.filter(d =>
    d.conf >= state.conf &&
    (!state.group || d.group === state.group) &&
    (!state.habitat || d.habitat === state.habitat) &&
    (!state.recorder || d.recorder === state.recorder) &&
    (!state.daynight || d.daynight === state.daynight) &&
    d.hour >= state.hourMin &&
    (!state.search || d.common.toLowerCase().includes(state.search) || d.species.toLowerCase().includes(state.search))
  )
  const s = state.sort
  out.sort((a, b) =>
    s === 'conf-asc' ? a.conf - b.conf :
    s === 'time-asc' ? a.time.localeCompare(b.time) :
    s === 'time-desc' ? b.time.localeCompare(a.time) :
    s === 'species' ? a.common.localeCompare(b.common) :
    b.conf - a.conf)
  return out
}

// ---- wavesurfer player (lazy) ----------------------------------------------
function mountPlayer(card, d) {
  card.querySelector('.open-btn').remove()
  const player = document.createElement('div'); player.className = 'player'
  const wrap = document.createElement('div'); wrap.className = 'ws-wrap'
  const wsEl = document.createElement('div'); wsEl.className = 'ws'
  wrap.appendChild(wsEl); player.appendChild(wrap)
  const bar = document.createElement('div'); bar.className = 'player-bar'
  bar.innerHTML = `
    <button class="play-det">▶ Play detection</button>
    <button class="play-full ghost">Play full clip</button>
    <span class="time">loading…</span>`
  player.appendChild(bar); card.appendChild(player)

  const ws = WaveSurfer.create({
    container: wsEl, height: 44, waveColor: '#bcd6b0', progressColor: '#2C5F2D',
    cursorColor: '#D7263D', cursorWidth: 2, minPxPerSec: 100,
    autoScroll: true, autoCenter: true, url: d.audio, sampleRate: 48000,
  })
  const regions = ws.registerPlugin(Regions.create())
  ws.registerPlugin(Spectrogram.create({
    height: 160, labels: true, fftSamples: 512, scale: 'linear', frequencyMax: 12000,
  }))

  const timeEl = bar.querySelector('.time')
  let stopAt = null
  ws.on('decode', () => {
    regions.addRegion({ start: d.start, end: d.end, color: 'rgba(215,38,61,0.15)', drag: false, resize: false })
    ws.setTime(Math.max(0, d.start - 0.15))
    timeEl.textContent = `detection ${d.start.toFixed(1)}–${d.end.toFixed(1)} s of ${ws.getDuration().toFixed(0)} s`
  })
  ws.on('timeupdate', (t) => { if (stopAt !== null && t >= stopAt) { ws.pause(); stopAt = null } })
  ws.on('play', () => { if (activeWs && activeWs !== ws) activeWs.pause(); activeWs = ws })

  bar.querySelector('.play-det').addEventListener('click', () => {
    ws.setTime(Math.max(0, d.start - 0.15)); stopAt = d.end + 0.15; ws.play()
  })
  bar.querySelector('.play-full').addEventListener('click', () => { stopAt = null; ws.playPause() })
}

// ---- rendering -------------------------------------------------------------
function card(d) {
  const el = document.createElement('div'); el.className = 'card'
  el.innerHTML = `
    <div class="card-head">
      <div class="sp">
        <span class="common">${d.common}</span>
        <span class="sci">${d.species}</span>
      </div>
      <span class="badge" style="background:${confColor(d.conf)}">${fmt(d.conf)}</span>
    </div>
    <div class="meta">
      ${d.group ? `<span class="tag taxon-${d.group}">${d.group === 'frog' ? '🐸' : d.group === 'insect' ? '🦗' : '🐦'} ${d.group}</span>` : ''}
      <span class="tag ${d.habitat}">${d.habitat} · ${d.recorder}</span>
      <span class="tag">${d.moth}</span>
      <span class="tag">${d.time}</span>
      <span class="tag">${d.daynight}</span>
    </div>
    <div class="hint">det ${d.start.toFixed(1)}–${d.end.toFixed(1)} s · click to load spectrogram + audio</div>
    <button class="open-btn">▶ Load spectrogram &amp; audio</button>`
  el.querySelector('.open-btn').addEventListener('click', () => mountPlayer(el, d))
  return el
}

function render() {
  const rows = filtered()
  const pages = Math.max(1, Math.ceil(rows.length / PAGE_SIZE))
  if (state.page >= pages) state.page = pages - 1
  const slice = rows.slice(state.page * PAGE_SIZE, state.page * PAGE_SIZE + PAGE_SIZE)

  $('counts').textContent = `${rows.length} of ${DATA.length} detections`
  const grid = $('grid'); grid.innerHTML = ''
  if (!slice.length) { grid.innerHTML = '<div class="empty">No detections match these filters.</div>' }
  else slice.forEach(d => grid.appendChild(card(d)))
  renderPager(rows.length, pages)
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function renderPager(total, pages) {
  const pager = $('pager'); pager.innerHTML = ''
  if (total === 0) return
  const mk = (label, page, opts = {}) => {
    const b = document.createElement('button'); b.textContent = label
    if (opts.active) b.classList.add('active')
    if (opts.disabled) b.disabled = true
    else b.addEventListener('click', () => { state.page = page; render() })
    return b
  }
  pager.appendChild(mk('‹ Prev', state.page - 1, { disabled: state.page === 0 }))
  const win = 3
  for (let p = 0; p < pages; p++) {
    if (p === 0 || p === pages - 1 || Math.abs(p - state.page) <= win) {
      pager.appendChild(mk(String(p + 1), p, { active: p === state.page }))
    } else if (Math.abs(p - state.page) === win + 1) {
      const s = document.createElement('span'); s.className = 'info'; s.textContent = '…'; pager.appendChild(s)
    }
  }
  pager.appendChild(mk('Next ›', state.page + 1, { disabled: state.page === pages - 1 }))
}

// ---- boot ------------------------------------------------------------------
if (!DATA.length) {
  $('grid').innerHTML = '<div class="empty">No data loaded. Run <code>Rscript build_gallery_site.R</code> to generate manifest.js, then reload.</div>'
  $('counts').textContent = '0 detections'
} else {
  $('foot').textContent = `${DATA.length} detections · ${META.species.length} species · generated ${META.generated || ''} · audio streamed from this PC`
  initControls(); render()
}
