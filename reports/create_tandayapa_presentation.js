const pptxgen = require('pptxgenjs');
const path = require('path');

const pptx = new pptxgen();
pptx.layout = 'LAYOUT_WIDE'; // 13.333 x 7.5
pptx.author = 'Franz Chandi, María Andrade, Priscila Cajas, Noemi Castro';
pptx.subject = 'Tandayapa acoustic recorder spacing experiment';
pptx.title = 'When do two AudioMoth recorders hear different communities?';
pptx.company = 'USFQ Tropical Ecology and Conservation';
pptx.lang = 'en-US';
pptx.theme = {
  headFontFace: 'Aptos Display',
  bodyFontFace: 'Aptos',
  lang: 'en-US'
};
pptx.margin = 0;
pptx.layout = 'LAYOUT_WIDE';
pptx.defineLayout({ name: 'CUSTOM_WIDE', width: 13.333, height: 7.5 });
pptx.layout = 'CUSTOM_WIDE';
pptx.slideWidth = 13.333;
pptx.slideHeight = 7.5;
pptx.notesSlide = { showNotes: true };
pptx.layout = 'LAYOUT_WIDE';

const ROOT = path.resolve(__dirname, '..');
const A = path.join(ROOT, 'outputs', 'analysis');
const IMG = {
  map: path.join(A, 'sampling_map_merged.png'),
  indexDist: path.join(A, 'fig_index_distance_clean.png'),
  diel: path.join(A, 'fig5_diel_indices.png'),
  richness: path.join(A, 'fig3_richness_by_habitat.png'),
  jaccard: path.join(A, 'fig_community_jaccard_clean.png'),
  micro: path.join(A, 'fig6_microclimate.png'),
};

const C = {
  forest: '123E2A',
  forest2: '1E5A3A',
  moss: '2C5F2D',
  pasture: 'D9A441',
  gold2: 'F0C96A',
  cream: 'F7F3E8',
  white: 'FFFFFF',
  ink: '102015',
  muted: 'CFE4D4',
  gray: 'E8EEE8',
  red: 'C74434',
};

function slideBase(slide, opts={}) {
  slide.background = { color: opts.bg || C.forest };
  slide.addShape(pptx.ShapeType.rect, { x:0, y:0, w:13.333, h:7.5, fill:{color:opts.bg || C.forest}, line:{color:opts.bg || C.forest} });
  if (!opts.noFooter) {
    slide.addText('Tandayapa recorder spacing experiment', { x:0.45, y:7.14, w:6.0, h:0.18, fontFace:'Aptos', fontSize:7.5, color:C.muted, margin:0 });
    slide.addText(String(opts.num || ''), { x:12.55, y:7.10, w:0.35, h:0.2, fontSize:8, color:C.muted, align:'right', margin:0 });
  }
}

function title(slide, text, sub='', opts={}) {
  slide.addText(text, { x:0.55, y:0.38, w:12.2, h:0.55, fontFace:'Aptos Display', fontSize:opts.size || 25, bold:true, color:opts.color || C.white, margin:0, breakLine:false, fit:'shrink' });
  if (sub) slide.addText(sub, { x:0.58, y:0.96, w:11.7, h:0.32, fontSize:11, color:opts.subColor || C.muted, margin:0, fit:'shrink' });
}

function notes(slide, speaker, secs, text) {
  slide.addNotes(`[${speaker} — ~${secs}s]\n${text}`);
}

function card(slide, x, y, w, h, heading, body, opts={}) {
  slide.addShape(pptx.ShapeType.roundRect, { x, y, w, h, rectRadius:0.12, fill:{color:opts.fill || C.cream, transparency: opts.transparency || 0}, line:{color:opts.line || 'FFFFFF', transparency: opts.lineTrans || 100}, shadow:{type:'outer', color:'000000', opacity:0.17, blur:1, angle:45, distance:1} });
  if (opts.accent !== false) slide.addShape(pptx.ShapeType.rect, {x, y, w:0.08, h, fill:{color: opts.accentColor || C.pasture}, line:{color: opts.accentColor || C.pasture}});
  slide.addText(heading, {x:x+0.22, y:y+0.15, w:w-0.38, h:0.34, fontSize:15, bold:true, color:opts.headingColor || C.forest, margin:0, fit:'shrink'});
  slide.addText(body, {x:x+0.22, y:y+0.58, w:w-0.38, h:h-0.75, fontSize:opts.bodySize || 11.5, color:opts.bodyColor || C.ink, margin:0.03, breakLine:false, fit:'shrink', valign:'mid'});
}

function iconCircle(slide, x, y, text, color=C.pasture) {
  slide.addShape(pptx.ShapeType.ellipse, {x, y, w:0.46, h:0.46, fill:{color}, line:{color:'FFFFFF', transparency:20}});
  slide.addText(text, {x, y: y+0.02, w:0.46, h:0.34, fontSize:12, bold:true, color:C.ink, align:'center', margin:0});
}

function addImage(slide, path, x, y, w, h, rounded=false) {
  slide.addImage({ path, x, y, w, h, sizing:{type:'contain', x, y, w, h} });
  if (rounded) slide.addShape(pptx.ShapeType.roundRect, {x, y, w, h, rectRadius:0.12, fill:{color:'FFFFFF', transparency:100}, line:{color:C.white, transparency:40, width:0.8}});
}

function effectTable(slide, x, y, w, rows, opts={}) {
  const data = rows.map((r, i) => r.map((c, j) => ({text:c, options:{
    bold: i===0,
    color: i===0 ? (opts.headerText || C.ink) : C.ink,
    fill: {color: i===0 ? (opts.header || C.pasture) : C.white, transparency: i===0 ? 0 : 0},
    margin: 0.04,
    fontSize: i===0 ? 10.5 : 9.2,
    breakLine:false,
  }})));
  slide.addTable(data, { x, y, w, h: opts.h || (0.36 * rows.length), colW: opts.colW, border:{type:'solid', color:'D7E0D8', pt:0.4}, margin:0.03, valign:'mid' });
}

function sectionLabel(slide, x, y, txt) {
  slide.addShape(pptx.ShapeType.roundRect, {x, y, w:1.15, h:0.34, rectRadius:0.08, fill:{color:C.pasture}, line:{color:C.pasture}});
  slide.addText(txt, {x:x+0.05, y:y+0.07, w:1.05, h:0.16, fontSize:8.5, bold:true, color:C.ink, align:'center', margin:0});
}

// 1 Title
{
  const s = pptx.addSlide(); slideBase(s,{noFooter:true});
  s.addShape(pptx.ShapeType.rect, {x:0, y:0, w:13.333, h:7.5, fill:{color:C.forest}, line:{color:C.forest}});
  s.addShape(pptx.ShapeType.arc, {x:7.4, y:-0.7, w:6.2, h:6.2, adjustPoint:0.2, line:{color:C.pasture, transparency:45, width:3}, fill:{color:C.forest2, transparency:65}});
  s.addShape(pptx.ShapeType.arc, {x:-1.4, y:4.4, w:4.0, h:4.0, line:{color:C.pasture, transparency:60, width:2}, fill:{color:C.forest2, transparency:85}});
  s.addText('WHEN DO TWO RECORDERS HEAR\nDIFFERENT COMMUNITIES?', {x:0.85, y:1.35, w:10.8, h:1.55, fontFace:'Aptos Display', fontSize:34, bold:true, color:C.white, margin:0, fit:'shrink'});
  s.addText('Acoustic recorder spacing in forest and pasture at Tandayapa Cloud Forest Station', {x:0.9, y:3.12, w:10.6, h:0.45, fontSize:17, color:C.muted, margin:0});
  s.addShape(pptx.ShapeType.rect, {x:0.9, y:3.82, w:2.2, h:0.08, fill:{color:C.pasture}, line:{color:C.pasture}});
  s.addText('Franz Chandi · María Andrade · Priscila Cajas · Noemi Castro\nTropical Ecology & Conservation · USFQ · June 2026', {x:0.9, y:4.25, w:8.8, h:0.65, fontSize:13.2, color:C.white, margin:0, breakLine:false});
  s.addText('15-minute scientific presentation', {x:0.9, y:6.85, w:4.1, h:0.25, fontSize:10, color:C.muted, margin:0});
  notes(s, 'María', 35, 'We are presenting a short field study from Tandayapa Cloud Forest Station. The practical problem is simple: if we put two AudioMoth recorders close together, are they hearing basically the same community, or do they capture different information? We tested that in forest and pasture using both acoustic indices and species-level detections.');
}

// 2 Introduction
{
 const s=pptx.addSlide(); slideBase(s,{num:2}); title(s,'Why recorder spacing matters','Passive acoustic monitoring is powerful, but deployment design can bias what we hear.');
 card(s,0.7,1.6,3.55,3.65,'Too close','Recorders may duplicate the same callers and waste batteries, storage, and field effort.',{bodySize:14});
 card(s,4.9,1.6,3.55,3.65,'Too far','We may miss spatial variation in vocal activity and community composition.',{bodySize:14});
 card(s,9.1,1.6,3.55,3.65,'Best design','Spacing should match the ecological signal and the metric being analyzed.',{bodySize:14});
 iconCircle(s,1.0,1.12,'1'); iconCircle(s,5.2,1.12,'2'); iconCircle(s,9.4,1.12,'3');
 s.addText('Core idea: “same soundscape” depends on the metric — indices and species community are not interchangeable.', {x:1.05,y:6.0,w:11.4,h:0.44,fontSize:16,bold:true,color:C.white,align:'center',margin:0});
 notes(s, 'María', 45, 'Passive acoustic monitoring lets us sample many places with little disturbance, but the spacing of recorders is a design choice. If recorders are too close, we collect redundant data; if they are too far, we may miss local changes. We wanted to ask this as a field question, not just a rule-of-thumb question, and compare two common ways of measuring the soundscape.');
}

// 3 Question
{
 const s=pptx.addSlide(); slideBase(s,{num:3}); title(s,'Research question','At what distance do two AudioMoths begin to capture different acoustic information?');
 s.addShape(pptx.ShapeType.roundRect,{x:0.85,y:1.55,w:5.4,h:4.7,rectRadius:0.16,fill:{color:C.cream},line:{color:C.cream}});
 s.addText('We measured “different” two ways', {x:1.15,y:1.86,w:4.7,h:0.35,fontSize:18,bold:true,color:C.forest,margin:0});
 card(s,1.18,2.55,4.55,1.25,'Acoustic indices','ACI, BI and ADI: cheap summaries of sound amount and structure.',{bodySize:12.5});
 card(s,1.18,4.15,4.55,1.25,'Species community','BirdNET detections converted to richness, activity and turnover.',{bodySize:12.5,accentColor:C.forest});
 s.addShape(pptx.ShapeType.roundRect,{x:7.0,y:1.55,w:5.45,h:4.7,rectRadius:0.16,fill:{color:C.forest2},line:{color:C.forest2}});
 s.addText('Main comparison', {x:7.35,y:1.88,w:4.6,h:0.35,fontSize:18,bold:true,color:C.white,margin:0});
 s.addText('Does the distance effect differ between habitats?', {x:7.35,y:2.55,w:4.7,h:0.5,fontSize:18,bold:true,color:C.white,margin:0,fit:'shrink'});
 s.addText('Forest', {x:7.6,y:3.55,w:1.45,h:0.35,fontSize:18,bold:true,color:C.white,align:'center',margin:0});
 s.addText('Pasture', {x:10.25,y:3.55,w:1.6,h:0.35,fontSize:18,bold:true,color:C.white,align:'center',margin:0});
 s.addShape(pptx.ShapeType.chevron,{x:9.25,y:3.48,w:0.68,h:0.52,fill:{color:C.pasture},line:{color:C.pasture}});
 s.addText('Same spacing, different habitat structure', {x:7.55,y:4.75,w:4.1,h:0.35,fontSize:13.5,color:C.muted,align:'center',margin:0});
 notes(s, 'María', 45, 'Our question was: at what distance do two recorders stop giving us the same information? We separated that into two types of response. First, acoustic indices: fast and cheap, but not species-specific. Second, the species community estimated by BirdNET, which is closer to a biodiversity question. We also asked whether forest and pasture behave differently.');
}

// 4 Predictions
{
 const s=pptx.addSlide(); slideBase(s,{num:4}); title(s,'Predictions','Three field predictions guided the analysis.');
 const preds=[['P1','Distance','Acoustic differences increase as recorders are placed farther apart.'],['P2','Habitat contrast','Differences increase faster in forest because dense vegetation should attenuate sound.'],['P3','Time of day','Between-recorder differences are greatest during dawn and daytime choruses.']];
 preds.forEach((p,i)=>{const x=0.85+i*4.15; card(s,x,1.65,3.55,4.45,p[0]+' · '+p[1],p[2],{bodySize:15,accentColor:i===1?C.forest:C.pasture}); s.addText(i===0?'↔':i===1?'🌳':'☀', {x:x+1.33,y:4.75,w:0.8,h:0.45,fontSize:25,align:'center',margin:0});});
 s.addText('We tested predictions with effect sizes and 95% confidence intervals, not only p-values.', {x:1.2,y:6.45,w:10.8,h:0.35,fontSize:16,bold:true,color:C.white,align:'center',margin:0});
 notes(s, 'María', 40, 'We made three predictions. First, recorders should become more different with distance. Second, we expected the effect to be stronger in forest, because vegetation can attenuate sound and create more acoustic structure. Third, we predicted that differences would be largest during biologically active periods like dawn and daytime chorus.');
}

// 5 Study area map
{
 const s=pptx.addSlide(); slideBase(s,{num:5}); title(s,'Study area: Tandayapa Cloud Forest Station','Chocó Andino, western Andes of Ecuador · ~1,650 m elevation');
 addImage(s, IMG.map, 0.55, 1.28, 12.25, 5.1, true);
 s.addShape(pptx.ShapeType.roundRect,{x:0.72,y:6.52,w:11.9,h:0.42,rectRadius:0.1,fill:{color:C.cream},line:{color:C.cream}});
 s.addText('Two adjacent habitats: secondary cloud forest (~79% canopy, cool/humid) and open pasture (~27% canopy, exposed).', {x:0.95,y:6.64,w:11.25,h:0.18,fontSize:11.6,bold:true,color:C.forest,align:'center',margin:0});
 notes(s, 'Franz', 50, 'This is the study area. The left panel shows the trail from Tandayapa Station to Domos and the location of our study area. The right panel zooms into the recorder layout. We sampled adjacent forest and pasture habitats, which makes the comparison useful because the sites are close, but have very different vegetation structure and microclimate.');
}

// 6 Noemi experimental design video
{
 const s=pptx.addSlide(); slideBase(s,{num:6}); title(s,'Experimental design — Noemi video','');
 s.addShape(pptx.ShapeType.roundRect,{x:3.0,y:1.55,w:7.35,h:4.55,rectRadius:0.2,fill:{color:C.cream},line:{color:C.pasture,width:2}});
 s.addText('▶', {x:5.85,y:2.35,w:1.6,h:1.4,fontSize:68,bold:true,color:C.forest,align:'center',margin:0});
 s.addText('[video by Noemi]', {x:3.75,y:4.25,w:5.85,h:0.45,fontSize:28,bold:true,color:C.forest,align:'center',margin:0});
 s.addText('Short 3-point transects · 15/30/60 m spacing · two replicate days per spacing', {x:3.35,y:5.1,w:6.7,h:0.32,fontSize:15,color:C.ink,align:'center',margin:0});
 notes(s, 'Noemi', 40, 'Video placeholder. Noemi explains the experimental design: AudioMoths on short transects, with 15, 30 and 60 meter spacings, replicated across days in forest and pasture.');
}

// 7 Noemi data collection video
{
 const s=pptx.addSlide(); slideBase(s,{num:7}); title(s,'Data collection — Noemi video','');
 s.addShape(pptx.ShapeType.roundRect,{x:3.0,y:1.55,w:7.35,h:4.55,rectRadius:0.2,fill:{color:C.cream},line:{color:C.pasture,width:2}});
 s.addText('▶', {x:5.85,y:2.35,w:1.6,h:1.4,fontSize:68,bold:true,color:C.forest,align:'center',margin:0});
 s.addText('[video by Noemi]', {x:3.75,y:4.25,w:5.85,h:0.45,fontSize:28,bold:true,color:C.forest,align:'center',margin:0});
 s.addText('29 recorders · 2–7 June 2026 · 3 two-minute clips per hour', {x:3.35,y:5.1,w:6.7,h:0.32,fontSize:15,color:C.ink,align:'center',margin:0});
 notes(s, 'Noemi', 40, 'Video placeholder. Noemi explains deployment, recorder schedules and field logistics: 29 AudioMoths, recording from late morning through the next morning, with three two-minute clips per hour.');
}

// 8 Analysis
{
 const s=pptx.addSlide(); slideBase(s,{num:8}); title(s,'Data analysis','We treated recorder pairs as the unit of spatial comparison.');
 card(s,0.7,1.45,3.8,4.55,'1 · Pairwise differences','For every within-habitat pair, calculate how different two recorders were in acoustic indices or species composition.',{bodySize:12.8});
 card(s,4.83,1.45,3.8,4.55,'2 · Mixed models','Distance model: response ~ distance + (1|deployment day). Time model also includes recorder pair.',{bodySize:12.8,accentColor:C.forest});
 card(s,8.96,1.45,3.8,4.55,'3 · Effect-size logic','Report slope per 10 m + 95% CI. Ecological threshold for Jaccard: ≥0.10 turnover over 60 m.',{bodySize:12.8});
 s.addText('Detectable ≠ important: we judged importance by magnitude, not just whether CI excluded zero.', {x:0.95,y:6.45,w:11.45,h:0.35,fontSize:15.3,bold:true,color:C.white,align:'center',margin:0});
 notes(s, 'Franz', 55, 'The analysis used recorder pairs, because our question is about how different two recorders are from each other. For each pair within a habitat, we calculated differences in acoustic indices and dissimilarity in species composition. We used linear mixed models with deployment day as a random effect. Importantly, we report slopes and confidence intervals, and we separate detectable effects from effects that are large enough to matter ecologically.');
}

// 9 indices vs distance
{
 const s=pptx.addSlide(); slideBase(s,{num:9}); title(s,'Results 1: acoustic indices did not change with distance','P1 was not supported for ACI, BI or ADI over 15–60 m.');
 addImage(s, IMG.indexDist, 0.55, 1.35, 7.25, 3.2, true);
 effectTable(s, 8.05, 1.48, 4.75, [
  ['Metric','Slope / 10 m','95% CI','Verdict'],
  ['ACI','−0.31','−1.34 to +0.72','Not meaningful'],
  ['BI','−0.07','−0.33 to +0.18','Not meaningful'],
  ['ADI','−0.008','−0.020 to +0.003','Not meaningful'],
 ], {colW:[1.0,1.15,1.55,1.05], h:1.55});
 card(s,0.85,5.0,11.65,1.2,'Interpretation','The slopes are near zero and the confidence intervals overlap zero. At this spatial scale, cheap acoustic indices were dominated by time-of-day variation, not recorder spacing.',{bodySize:13.2,accentColor:C.pasture});
 notes(s, 'Franz', 55, 'The first result is negative but important. For ACI, BI and ADI, the slopes with distance are all close to zero and the confidence intervals include zero. This means we did not detect a distance effect for acoustic indices between 15 and 60 meters. In practical terms, these indices alone would tell us that recorder spacing did not matter much at this scale.');
}

// 10 habitat contrast explainer
{
 const s=pptx.addSlide(); slideBase(s,{num:10}); title(s,'Do habitats differ in the distance slope?','Interactive models test whether forest and pasture have different spatial decay.');
 s.addShape(pptx.ShapeType.roundRect,{x:0.9,y:1.45,w:5.15,h:4.65,rectRadius:0.18,fill:{color:C.cream},line:{color:C.cream}});
 s.addText('Acoustic indices', {x:1.25,y:1.85,w:4.2,h:0.35,fontSize:20,bold:true,color:C.forest,margin:0});
 s.addText('Additive model preferred', {x:1.25,y:2.48,w:4.1,h:0.4,fontSize:25,bold:true,color:C.pasture,margin:0});
 s.addText('Distance slopes do not clearly differ by habitat for ACI, BI or ADI.', {x:1.25,y:3.15,w:4.15,h:1.0,fontSize:16,color:C.ink,margin:0,fit:'shrink'});
 s.addShape(pptx.ShapeType.roundRect,{x:7.05,y:1.45,w:5.15,h:4.65,rectRadius:0.18,fill:{color:C.cream},line:{color:C.cream}});
 s.addText('Community turnover', {x:7.4,y:1.85,w:4.2,h:0.35,fontSize:20,bold:true,color:C.forest,margin:0});
 s.addText('Only marginal contrast', {x:7.4,y:2.48,w:4.1,h:0.4,fontSize:25,bold:true,color:C.pasture,margin:0});
 s.addText('Pasture shows the clearest distance-decay, but a difference in significance is not automatically a significant habitat difference.', {x:7.4,y:3.15,w:4.2,h:1.2,fontSize:15.5,color:C.ink,margin:0,fit:'shrink'});
 s.addText('Honest wording: “dissimilarity rises with distance, most clearly in pasture.”', {x:1.2,y:6.55,w:11.0,h:0.28,fontSize:15.5,bold:true,color:C.white,align:'center',margin:0});
 notes(s, 'Franz', 45, 'We also compared additive and interactive models. For the indices, there is no strong evidence that the distance slope differs between forest and pasture. For community turnover, the pasture slope is clearer than the forest slope, but the formal habitat interaction is only marginal. So the honest wording is that dissimilarity rises with distance, most clearly in pasture, not that we proved a definitive habitat difference.');
}

// 11 time of day
{
 const s=pptx.addSlide(); slideBase(s,{num:11}); title(s,'Results 2: acoustic indices changed strongly by time of day','P3 was supported: dawn/day chorus dominated index differences.');
 addImage(s, IMG.diel, 0.65, 1.35, 7.0, 3.45, true);
 effectTable(s, 8.05, 1.45, 4.75, [
  ['Period vs night','BI diff.','95% CI','Detectable?'],
  ['Dawn','+1.15','+0.16 to +2.13','Yes'],
  ['Day','+1.35','+0.37 to +2.34','Yes'],
  ['Dusk','+1.02','+0.03 to +2.00','Yes'],
 ], {colW:[1.35,0.9,1.55,0.95], h:1.55});
 card(s,0.85,5.15,11.65,1.1,'Interpretation','Time of day explained more variation in acoustic indices than recorder distance. Recorders must be balanced across time periods to avoid confounding chorus effects with space.',{bodySize:13.2});
 notes(s, 'Priscila', 50, 'The indices did respond strongly to time of day. Biological Index was higher at dawn, during the day and at dusk compared with night, and the confidence intervals exclude zero. This supports prediction three. The key design message is that time of day must be balanced across recorders, because a dawn chorus can produce larger differences than moving a recorder tens of meters.');
}

// 12 richness/activity
{
 const s=pptx.addSlide(); slideBase(s,{num:12}); title(s,'Results 3: richness was similar, but vocal activity was higher in pasture','BirdNET separates biodiversity structure from how much animals were calling.');
 addImage(s, IMG.richness, 0.75, 1.35, 6.4, 4.25, true);
 card(s,7.65,1.42,4.9,1.25,'Species richness','Forest: 54 species · Pasture: 57 species — nearly equal.',{bodySize:14});
 card(s,7.65,3.02,4.9,1.25,'Vocal activity','Forest: 3,684 detections · Pasture: 5,214 detections.',{bodySize:14,accentColor:C.forest});
 card(s,7.65,4.62,4.9,1.25,'Interpretation','More detections in pasture likely reflect open sound transmission and calling activity, not necessarily higher biodiversity.',{bodySize:12.5});
 notes(s, 'Priscila', 50, 'The species results show why we should not treat detections as abundance. Richness was almost the same in forest and pasture, with 54 versus 57 detected species. However, pasture had many more detections, especially frogs and birds. That likely reflects more vocal activity and better sound propagation in open habitat, not that pasture has higher biodiversity.');
}

// 13 community distance decay
{
 const s=pptx.addSlide(); slideBase(s,{num:13}); title(s,'Results 4: species communities changed with distance — most clearly in pasture','This is the spatial signal the acoustic indices missed.');
 addImage(s, IMG.jaccard, 0.65, 1.32, 6.5, 4.25, true);
 effectTable(s, 7.5, 1.47, 5.05, [
  ['Habitat','Jaccard slope / 10 m','95% CI','60 m effect'],
  ['Pasture','+0.060','+0.012 to +0.108','+0.36 · meaningful'],
  ['Forest','+0.011','−0.018 to +0.039','+0.07 · not meaningful'],
  ['Threshold','','≥0.10 over 60 m','pre-defined'],
 ], {colW:[1.05,1.55,1.55,1.05], h:1.55});
 card(s,7.75,4.72,4.55,1.25,'Careful interpretation','This is opposite of P2, but the formal habitat contrast is marginal. Say: distance-decay is strongest/clearest in pasture.',{bodySize:12.2,accentColor:C.pasture});
 notes(s, 'Franz', 60, 'The community analysis gives the strongest spatial result. In pasture, Jaccard dissimilarity increased by about 0.060 per 10 meters, which is about 0.36 over 60 meters. That exceeds our 0.10 ecological threshold. Forest had a much smaller slope and its confidence interval included zero. This is the opposite of our forest attenuation prediction, but we should be careful: the formal habitat interaction is only marginal, so the best claim is that distance-decay is clearest in pasture.');
}

// 14 synthesis
{
 const s=pptx.addSlide(); slideBase(s,{num:14}); title(s,'Main synthesis','Indices and species community answered different parts of the design question.');
 s.addShape(pptx.ShapeType.roundRect,{x:0.85,y:1.45,w:5.45,h:4.5,rectRadius:0.18,fill:{color:C.cream},line:{color:C.cream}});
 s.addText('Acoustic indices', {x:1.25,y:1.85,w:4.5,h:0.4,fontSize:23,bold:true,color:C.forest,margin:0});
 s.addText('Track time', {x:1.25,y:2.65,w:4.5,h:0.48,fontSize:34,bold:true,color:C.forest,margin:0});
 s.addText('Best for broad temporal questions such as dawn/day chorus strength.', {x:1.25,y:3.55,w:4.3,h:0.7,fontSize:15,color:C.ink,margin:0,fit:'shrink'});
 s.addShape(pptx.ShapeType.roundRect,{x:7.02,y:1.45,w:5.45,h:4.5,rectRadius:0.18,fill:{color:C.cream},line:{color:C.cream}});
 s.addText('Species community', {x:7.42,y:1.85,w:4.5,h:0.4,fontSize:23,bold:true,color:C.forest,margin:0});
 s.addText('Tracks space', {x:7.42,y:2.65,w:4.5,h:0.48,fontSize:34,bold:true,color:C.forest,margin:0});
 s.addText('Needed for biodiversity questions about whether recorders sample different communities.', {x:7.42,y:3.55,w:4.3,h:0.7,fontSize:15,color:C.ink,margin:0,fit:'shrink'});
 s.addText('Complementary, not redundant.', {x:3.7,y:6.48,w:5.9,h:0.35,fontSize:19,bold:true,color:C.white,align:'center',margin:0});
 notes(s, 'Franz', 45, 'The overall message is that these two data currencies are complementary. Acoustic indices are useful, but in this experiment they mostly tracked time of day, not space. Species community data captured spatial turnover, especially in pasture. So for deployment design, the metric matters: if the question is biodiversity or community composition, species-level data are necessary.');
}

// 15 limitations
{
 const s=pptx.addSlide(); slideBase(s,{num:15}); title(s,'Limitations','These results are useful, but we should not overclaim.');
 const lims=[['Sample size','Only 10–12 independent pairs per habitat; some recorder failures.'],['Spatial scale','Analysis capped at 60 m because field layout and habitat size limited wider spacing.'],['Independence','Pairs within a day can share recorders, so observations are not fully independent.'],['Interpretation','BirdNET detections measure vocal activity, not true abundance; one logger per habitat.']];
 lims.forEach((l,i)=>card(s,0.75+(i%2)*6.05,1.48+Math.floor(i/2)*2.28,5.35,1.55,l[0],l[1],{bodySize:13.2,accentColor:i%2?C.forest:C.pasture}));
 s.addText('Best use: a pilot result that guides stronger replicated sampling, not a universal spacing rule.', {x:1.1,y:6.55,w:11.1,h:0.3,fontSize:15.3,bold:true,color:C.white,align:'center',margin:0});
 notes(s, 'Priscila', 45, 'There are several limitations. The number of independent pairs is small, and recorder failures reduced the design. We were also limited to 60 meters, so the study cannot tell us what happens at 100 or 200 meters. BirdNET detections are vocal activity, not true abundance. Therefore, this is best presented as a strong pilot and design study, not a universal rule for all cloud forest monitoring.');
}

// 16 Future Noemi video
{
 const s=pptx.addSlide(); slideBase(s,{num:16}); title(s,'Future directions — Noemi video','');
 s.addShape(pptx.ShapeType.roundRect,{x:3.0,y:1.55,w:7.35,h:4.55,rectRadius:0.2,fill:{color:C.cream},line:{color:C.pasture,width:2}});
 s.addText('▶', {x:5.85,y:2.35,w:1.6,h:1.4,fontSize:68,bold:true,color:C.forest,align:'center',margin:0});
 s.addText('[video by Noemi]', {x:3.75,y:4.25,w:5.85,h:0.45,fontSize:28,bold:true,color:C.forest,align:'center',margin:0});
 s.addText('More days · independent transects · local classifier tuning · vegetation/weather sensors', {x:3.1,y:5.1,w:7.1,h:0.32,fontSize:15,color:C.ink,align:'center',margin:0});
 notes(s, 'Noemi', 40, 'Video placeholder. Noemi explains future work: replicate spacings on independent transects, add more days, improve local classifier validation, and measure vegetation and weather more directly.');
}

// 17 Thank you
{
 const s=pptx.addSlide(); slideBase(s,{num:17,noFooter:true});
 s.addShape(pptx.ShapeType.rect,{x:0,y:0,w:13.333,h:7.5,fill:{color:C.forest},line:{color:C.forest}});
 s.addText('Thank you', {x:0.85,y:0.9,w:11.7,h:0.7,fontSize:44,bold:true,color:C.white,align:'center',margin:0});
 s.addText('Three take-home messages', {x:0.85,y:1.75,w:11.7,h:0.35,fontSize:17,color:C.pasture,bold:true,align:'center',margin:0});
 card(s,1.0,2.55,3.55,2.2,'1','Indices track time more than space at 15–60 m.',{bodySize:17});
 card(s,4.9,2.55,3.55,2.2,'2','Species community detects spatial turnover, clearest in pasture.',{bodySize:17,accentColor:C.forest});
 card(s,8.8,2.55,3.55,2.2,'3','Biodiversity spacing questions need species-level data.',{bodySize:17});
 s.addText('Questions?', {x:4.4,y:6.18,w:4.5,h:0.45,fontSize:30,bold:true,color:C.white,align:'center',margin:0});
 notes(s, 'All', 30, 'Our main takeaways are simple. At this scale, acoustic indices did not change with distance, but they changed strongly with time of day. Species community data did reveal spatial turnover, especially in pasture. So the best recorder design depends on the ecological question and on whether we are measuring general sound structure or species composition.');
}

// 18 closing video
{
 const s=pptx.addSlide(); slideBase(s,{num:18,noFooter:true});
 s.addShape(pptx.ShapeType.rect,{x:0,y:0,w:13.333,h:7.5,fill:{color:C.forest},line:{color:C.forest}});
 s.addText('Closing video', {x:0.9,y:0.85,w:11.5,h:0.6,fontSize:38,bold:true,color:C.white,align:'center',margin:0});
 s.addShape(pptx.ShapeType.roundRect,{x:3.3,y:2.0,w:6.75,h:3.85,rectRadius:0.22,fill:{color:C.cream},line:{color:C.pasture,width:2}});
 s.addText('▶', {x:5.85,y:2.55,w:1.6,h:1.35,fontSize:68,bold:true,color:C.pasture,align:'center',margin:0});
 s.addText('[team soundscape / photos video]', {x:3.85,y:4.25,w:5.65,h:0.4,fontSize:22,bold:true,color:C.forest,align:'center',margin:0});
 s.addText('Short, optional closing clip with field photos and sounds.', {x:3.75,y:5.0,w:5.85,h:0.3,fontSize:15,color:C.ink,align:'center',margin:0});
 notes(s, 'All', 20, 'Optional closing video. If there is no time, skip this slide and finish with the thank-you slide.');
}

pptx.writeFile({ fileName: path.join(ROOT, 'reports', 'tandayapa_spacing_presentation_improved.pptx') });
