/* ═══ 路焉识设计工作站 v7.0 ═══ */
const { createApp, ref, computed, onMounted } = Vue;

createApp({
  setup() {
    const currentPage = ref('dashboard');
    const globalSearch = ref('');
    const searchResults = ref([]);
    const currentTime = ref('');
    setInterval(() => {
      const d = new Date();
      currentTime.value = d.toLocaleDateString('zh-CN') + ' ' + d.toLocaleTimeString('zh-CN', { hour:'2-digit', minute:'2-digit', second:'2-digit' });
    }, 1000);
    const navItems = [
      { id: 'dashboard', label: '首页' },
      { id: 'projects', label: '项目' },
      { id: 'clients', label: '客户' },
      { id: 'inspiration', label: '灵感' },
      { id: 'ai', label: 'AI 生图' },
      { id: 'agents', label: 'Agent' },
      { id: 'materials', label: '材料' },
      { id: 'colors', label: '配色' },
      { id: 'dimensions', label: '尺寸' },
      { id: 'pricing', label: '报价' },
    ];

    async function api(url, opts = {}) {
      const res = await fetch(url, { headers: { 'Content-Type': 'application/json', ...opts.headers }, ...opts, body: opts.body ? JSON.stringify(opts.body) : undefined });
      return res.json();
    }
    function statusClass(s) { return { '接洽中':'status-blue','量房':'status-yellow','方案':'status-blue','深化':'status-purple','施工':'status-green','完工':'status-green' }[s]||'status-blue'; }

    // 搜索
    function doSearch() {
      const q = globalSearch.value.toLowerCase().trim();
      if (!q) { searchResults.value = []; return; }
      const r = [];
      projects.value.forEach(p => { if ((p.name||'').toLowerCase().includes(q)||(p.client_name||'').toLowerCase().includes(q)) r.push({id:p.id,type:'项目',title:p.name,sub:`${p.client_name||''} · ${p.style||''}`,action:()=>viewProject(p)}); });
      clients.value.forEach(c => { if ((c.name||'').toLowerCase().includes(q)||(c.phone||'').includes(q)) r.push({id:c.id,type:'客户',title:c.name,sub:c.phone||'',action:()=>{currentPage.value='clients'}}); });
      inspirations.value.forEach(i => { if ((i.title||'').toLowerCase().includes(q)||(i.tags||[]).some(t=>t.toLowerCase().includes(q))) r.push({id:i.id,type:'灵感',title:i.title,sub:(i.description||'').slice(0,40),action:()=>{currentPage.value='inspiration'}}); });
      materials.value.forEach(m => { if ((m.name||'').toLowerCase().includes(q)||(m.brand||'').toLowerCase().includes(q)) r.push({id:m.id,type:'材料',title:m.name,sub:m.brand||'',action:()=>{currentPage.value='materials'}}); });
      searchResults.value = r;
    }

    // 项目
    const projects = ref([]); const projectFilter = ref('全部'); const selectedProject = ref(null); const showNewProject = ref(false); const newProject = ref({}); const newNote = ref('');
    const filteredProjects = computed(() => projectFilter.value==='全部'?projects.value:projects.value.filter(p=>p.status===projectFilter.value));
    async function loadProjects() { projects.value = await api('/api/projects/'); }
    async function createProject() { if (!newProject.value.name) return; await api('/api/projects/',{method:'POST',body:newProject.value}); showNewProject.value=false; newProject.value={}; await loadProjects(); }
    async function viewProject(p) { selectedProject.value = await api(`/api/projects/${p.id}`); currentPage.value='projects'; globalSearch.value=''; searchResults.value=[]; }
    async function updateProjectStatus() { await api(`/api/projects/${selectedProject.value.id}`,{method:'PUT',body:{status:selectedProject.value.status}}); await loadProjects(); }
    async function deleteProject(id) { if (!confirm('确认删除？')) return; await api(`/api/projects/${id}`,{method:'DELETE'}); selectedProject.value=null; await loadProjects(); }
    async function addNote() { if (!newNote.value.trim()) return; await api(`/api/projects/${selectedProject.value.id}/notes`,{method:'POST',body:{content:newNote.value}}); newNote.value=''; selectedProject.value=await api(`/api/projects/${selectedProject.value.id}`); }
    async function handleUpload(e) { const files=e.target.files||e.dataTransfer?.files; if(!files) return; for(const f of files){const fd=new FormData();fd.append('file',f);fd.append('file_type','其他');await fetch(`/api/projects/${selectedProject.value.id}/files`,{method:'POST',body:fd});} selectedProject.value=await api(`/api/projects/${selectedProject.value.id}`); }
    function handleDrop(e) { handleUpload(e); }
    function getFileIcon(t) { return {'图纸':'📐','效果图':'🖼','报价':'💰','合同':'📄','现场照片':'📸'}[t]||'📎'; }
    function exportProjects() {
      const data = projects.value.map(p => ({名称:p.name,客户:p.client_name,地址:p.address,面积:p.area,风格:p.style,预算:p.budget,状态:p.status}));
      const csv = '\uFEFF' + ['名称,客户,地址,面积,风格,预算,状态', ...data.map(d => Object.values(d).join(','))].join('\n');
      const blob = new Blob([csv], {type:'text/csv;charset=utf-8;'}); const url = URL.createObjectURL(blob);
      const a = document.createElement('a'); a.href=url; a.download='项目列表.csv'; a.click(); URL.revokeObjectURL(url);
    }

    // 客户
    const clients = ref([]); const showNewClient = ref(false); const editingClient = ref(null); const clientForm = ref({});
    async function loadClients() { clients.value = await api('/api/clients/'); }
    function editClient(c) { editingClient.value=c; clientForm.value={...c}; showNewClient.value=true; }
    async function saveClient() { if(!clientForm.value.name) return; if(editingClient.value) await api(`/api/clients/${editingClient.value.id}`,{method:'PUT',body:clientForm.value}); else await api('/api/clients/',{method:'POST',body:clientForm.value}); showNewClient.value=false; editingClient.value=null; clientForm.value={}; await loadClients(); }
    async function deleteClient(id) { if(!confirm('确认删除？'))return; await api(`/api/clients/${id}`,{method:'DELETE'}); await loadClients(); }
    function getClientProjects(name) { return projects.value.filter(p=>p.client_name===name); }

    // 灵感
    const inspirations = ref([]); const inspFilter = ref('全部'); const showNewInspiration = ref(false); const newInsp = ref({tagsInput:''});
    const inspTab = ref('online');
    const onlineInspirations = ref([]); const onlineSources = ref([]); const selectedInspirations = ref([]);
    const updateStatus = ref({}); const isUpdating = ref(false);
    const filteredInspirations = computed(() => inspFilter.value==='全部'?inspirations.value:inspirations.value.filter(i=>i.category===inspFilter.value));
    async function loadInspirations() { inspirations.value = await api('/api/inspirations/'); }
    async function loadOnlineInspirations() { const res = await api('/api/online/online/inspirations'); onlineInspirations.value = res.items || []; onlineSources.value = await api('/api/online/sources'); updateStatus.value = await api('/api/online/update/status'); }
    async function createInspiration() { const tags=newInsp.value.tagsInput?newInsp.value.tagsInput.split(/[,，]/).map(s=>s.trim()).filter(Boolean):[]; await api('/api/inspirations/',{method:'POST',body:{...newInsp.value,tags,tagsInput:undefined}}); showNewInspiration.value=false; newInsp.value={tagsInput:''}; await loadInspirations(); }
    async function deleteInspiration(id) { await api(`/api/inspirations/${id}`,{method:'DELETE'}); await loadInspirations(); }
    async function importSingleInspiration(idx) { await api(`/api/online/import/inspiration/${idx}`,{method:'POST'}); await loadInspirations(); alert('导入成功！'); }
    function toggleSelectInspiration(idx) { const i=selectedInspirations.value.indexOf(idx); if(i>=0) selectedInspirations.value.splice(i,1); else selectedInspirations.value.push(idx); }
    function selectAllInspirations() { selectedInspirations.value = onlineInspirations.value.map((_,i)=>i); }
    async function batchImportInspirations() { await api('/api/online/import/inspirations/batch',{method:'POST',body:selectedInspirations.value}); selectedInspirations.value=[]; await loadInspirations(); alert('批量导入完成！'); }
    async function forceUpdate() { isUpdating.value=true; try { await api('/api/online/update/force',{method:'POST'}); await loadOnlineInspirations(); alert('更新完成！'); } finally { isUpdating.value=false; } }

    // AI
    const aiGen = ref({prompt:'',negative_prompt:'',style:'',mode:'txt2img',width:1024,height:1024});
    const aiStyles = ref([]); const aiHistory = ref([]); const aiMessage = ref('');
    async function loadAI() { aiStyles.value=await api('/api/ai/styles'); aiHistory.value=await api('/api/ai/history'); }
    async function generateImage() { aiMessage.value='正在生成...'; const res=await api('/api/ai/generate',{method:'POST',body:aiGen.value}); aiMessage.value=res.message||'已提交'; aiHistory.value=await api('/api/ai/history'); }

    // Agent
    const agents = ref([]); const showNewAgent = ref(false); const editingAgent = ref(null);
    const agentForm = ref({name:'',display_name:'',role:'设计',system_prompt:'',capabilitiesInput:'',red_linesInput:'',autonomy_level:'执行'});
    async function loadAgents() { agents.value = await api('/api/agents/'); }
    function editAgent(a) { editingAgent.value=a; agentForm.value={name:a.name,display_name:a.display_name,role:a.role,system_prompt:a.system_prompt,capabilitiesInput:(a.capabilities||[]).join(', '),red_linesInput:(a.red_lines||[]).join(', '),autonomy_level:a.autonomy_level}; showNewAgent.value=true; }
    async function saveAgent() { const body={...agentForm.value,capabilities:agentForm.value.capabilitiesInput.split(/[,，]/).map(s=>s.trim()).filter(Boolean),red_lines:agentForm.value.red_linesInput.split(/[,，]/).map(s=>s.trim()).filter(Boolean),capabilitiesInput:undefined,red_linesInput:undefined}; if(editingAgent.value) await api(`/api/agents/${editingAgent.value.id}`,{method:'PUT',body}); else await api('/api/agents/',{method:'POST',body}); showNewAgent.value=false; editingAgent.value=null; agentForm.value={name:'',display_name:'',role:'设计',system_prompt:'',capabilitiesInput:'',red_linesInput:'',autonomy_level:'执行'}; await loadAgents(); }
    async function deleteAgent(id) { if(!confirm('确认删除？'))return; await api(`/api/agents/${id}`,{method:'DELETE'}); await loadAgents(); }
    function getAgentColor(role) { return {'设计':'#1677ff','商务':'#00b42a','审查':'#f53f3f','内容':'#722ed1','助手':'#faad14'}[role]||'#86909c'; }

    // 材料
    const materials = ref([]); const matFilter = ref('全部'); const showNewMaterial = ref(false); const newMat = ref({});
    const matTab = ref('online'); const onlineMatFilter = ref('全部'); const onlineMaterials = ref([]);
    const filteredMaterials = computed(() => matFilter.value==='全部'?materials.value:materials.value.filter(m=>m.category===matFilter.value));
    const filteredOnlineMaterials = computed(() => onlineMatFilter.value==='全部'?onlineMaterials.value:onlineMaterials.value.filter(m=>m.category===onlineMatFilter.value));
    async function loadMaterials() { materials.value = await api('/api/materials/'); }
    async function loadOnlineMaterials() { const res = await api('/api/online/online/materials'); onlineMaterials.value = res.items || []; }
    async function createMaterial() { if(!newMat.value.name)return; await api('/api/materials/',{method:'POST',body:newMat.value}); showNewMaterial.value=false; newMat.value={}; await loadMaterials(); }
    async function deleteMaterial(id) { await api(`/api/materials/${id}`,{method:'DELETE'}); await loadMaterials(); }
    async function importSingleMaterial(idx) { await api(`/api/online/import/material/${idx}`,{method:'POST'}); await loadMaterials(); alert('导入成功！'); }

    // 配色工具
    const customColor = ref('#1677ff');
    const harmonyColors = ref([]);
    const colorPalettes = [
      { name:'现代简约', desc:'黑白灰+木色，干净利落', colors:['#2C2C2C','#F5F5F5','#D4A853','#8B7355','#FFFFFF'] },
      { name:'侘寂风', desc:'大地色系，自然质朴', colors:['#3D3D3D','#C4B59D','#E8DDD3','#A89F91','#F5F0EB'] },
      { name:'北欧风', desc:'清新明亮，蓝白为主', colors:['#1A1A2E','#E8F0FE','#5B8FB9','#F8F9FA','#FFFFFF'] },
      { name:'新中式', desc:'深木色+朱红，沉稳大气', colors:['#2B1B17','#8B4513','#C0392B','#F5E6D3','#FFFFFF'] },
      { name:'法式轻奢', desc:'金+墨绿，优雅复古', colors:['#1B4332','#D4A853','#F5F0E8','#2D6A4F','#FFFFFF'] },
      { name:'工业风', desc:'深灰+铁锈色，粗犷个性', colors:['#1A1A1A','#6B6B6B','#B7410E','#D4D4D4','#F0F0F0'] },
      { name:'奶油风', desc:'暖白+米色，温柔治愈', colors:['#F5F0E8','#E8DDD3','#D4C5B0','#FFFFFF','#C9B99A'] },
      { name:'莫兰迪', desc:'低饱和灰调，高级感', colors:['#7B8794','#A8B5C2','#C9D1D9','#E8B4B8','#B8C9A3'] },
      { name:'日式原木', desc:'浅木+白，温暖自然', colors:['#D4A853','#E8DDD3','#F5F0EB','#8B7355','#FFFFFF'] },
      { name:'复古港风', desc:'深红+墨绿，浓郁怀旧', colors:['#800020','#1B4332','#D4A853','#2C2C2C','#F5E6D3'] },
    ];
    function generateHarmony() {
      const hex = customColor.value;
      const r = parseInt(hex.slice(1,3),16), g = parseInt(hex.slice(3,5),16), b = parseInt(hex.slice(5,7),16);
      const hsl = rgbToHsl(r,g,b);
      const h = hsl[0], s = hsl[1], l = hsl[2];
      harmonyColors.value = [
        hex,
        hslToHex((h+30)%360, s, l),
        hslToHex((h+60)%360, s, l),
        hslToHex((h+180)%360, s, l),
        hslToHex(h, s, Math.min(95, l+30)),
        hslToHex(h, Math.max(10, s-20), l),
      ];
    }
    function rgbToHsl(r,g,b) { r/=255;g/=255;b/=255;const max=Math.max(r,g,b),min=Math.min(r,g,b);let h,s,l=(max+min)/2; if(max===min){h=s=0;}else{const d=max-min;s=l>0.5?d/(2-max-min):d/(max+min);switch(max){case r:h=((g-b)/d+(g<b?6:0))/6;break;case g:h=((b-r)/d+2)/6;break;case b:h=((r-g)/d+4)/6;break;}} return [Math.round(h*360),Math.round(s*100),Math.round(l*100)]; }
    function hslToHex(h,s,l) { s/=100;l/=100;const a=s*Math.min(l,1-l);const f=n=>{const k=(n+h/30)%12;return l-a*Math.max(Math.min(k-3,9-k,1),-1);};return `#${Math.round(f(0)*255).toString(16).padStart(2,'0')}${Math.round(f(8)*255).toString(16).padStart(2,'0')}${Math.round(f(4)*255).toString(16).padStart(2,'0')}`; }
    function copyColor(c) { navigator.clipboard?.writeText(c); }
    function copyPalette(p) { navigator.clipboard?.writeText(p.colors.join(', ')); }

    // 尺寸速查
    const dimSearch = ref('');
    const dimFilter = ref('全部');
    const dimensionData = [
      { name:'客厅', icon:'🛋', items:[{label:'沙发座高',value:'35-42cm'},{label:'茶几高度',value:'40-45cm'},{label:'电视柜高度',value:'40-60cm'},{label:'沙发与电视距离',value:'电视尺寸×3'},{label:'主通道宽度',value:'≥90cm'},{label:'吊灯离地',value:'≥220cm'}] },
      { name:'餐厅', icon:'🍽', items:[{label:'餐桌高度',value:'72-78cm'},{label:'餐椅座高',value:'43-45cm'},{label:'餐桌每人宽度',value:'≥60cm'},{label:'吊灯离桌面',value:'65-80cm'},{label:'餐边柜深度',value:'35-45cm'},{label:'过道宽度',value:'≥75cm'}] },
      { name:'卧室', icon:'🛏', items:[{label:'床面高度',value:'45-55cm'},{label:'衣柜深度',value:'55-60cm'},{label:'床头柜高度',value:'与床面齐平'},{label:'梳妆台高度',value:'70-75cm'},{label:'床侧过道',value:'≥60cm'},{label:'衣柜过道',value:'≥80cm'}] },
      { name:'厨房', icon:'🍳', items:[{label:'台面高度',value:'80-90cm'},{label:'吊柜底部离地',value:'≥155cm'},{label:'操作通道',value:'≥90cm'},{label:'灶台与水槽间距',value:'≥60cm'},{label:'台面深度',value:'55-65cm'},{label:'吊柜深度',value:'30-35cm'}] },
      { name:'卫生间', icon:'🚿', items:[{label:'洗手台高度',value:'80-85cm'},{label:'镜柜底部离地',value:'≥135cm'},{label:'马桶中心距墙',value:'≥37cm'},{label:'淋浴区最小',value:'90×90cm'},{label:'浴缸长度',value:'150-170cm'},{label:'毛巾架高度',value:'120-140cm'}] },
      { name:'通用', icon:'📏', items:[{label:'门洞宽度',value:'80-90cm'},{label:'走廊宽度',value:'≥100cm'},{label:'开关高度',value:'130-140cm'},{label:'插座高度',value:'30-40cm'},{label:'踢脚线高度',value:'8-12cm'},{label:'层高建议',value:'≥2.7m'}] },
    ];
    const filteredDimensions = computed(() => {
      let data = dimensionData;
      if (dimFilter.value !== '全部') data = data.filter(c => c.name === dimFilter.value);
      if (dimSearch.value.trim()) {
        const q = dimSearch.value.trim().toLowerCase();
        data = data.map(c => ({...c, items: c.items.filter(i => i.label.toLowerCase().includes(q) || i.value.toLowerCase().includes(q))})).filter(c => c.items.length > 0);
      }
      return data;
    });

    // 报价估算
    const priceCalc = ref({ area: 100, style: 'modern', grade: 'standard', multiplier: 1500, extras: [] });
    const styleMultipliers = { modern: 1.0, scandinavian: 1.05, japandi: 1.1, chinese: 1.2, french: 1.3, industrial: 0.95 };
    const styleMultiplier = computed(() => styleMultipliers[priceCalc.value.style] || 1.0);
    const baseCost = computed(() => (priceCalc.value.area || 0) * priceCalc.value.multiplier * styleMultiplier.value);
    const extrasData = { kitchen: 20000, bathroom: 15000, smart: 30000, custom: 25000 };
    const extrasCost = computed(() => priceCalc.value.extras.reduce((sum, id) => sum + (extrasData[id] || 0), 0));
    const estimatedTotal = computed(() => baseCost.value + extrasCost.value);
    function toggleExtra(id) {
      const idx = priceCalc.value.extras.indexOf(id);
      if (idx >= 0) priceCalc.value.extras.splice(idx, 1);
      else priceCalc.value.extras.push(id);
    }

    onMounted(async () => { await Promise.all([loadProjects(),loadClients(),loadInspirations(),loadOnlineInspirations(),loadAI(),loadAgents(),loadMaterials(),loadOnlineMaterials()]); });

    return {
      currentPage, navItems, globalSearch, searchResults, doSearch, statusClass, currentTime,
      projects, projectFilter, filteredProjects, selectedProject, showNewProject, newProject, newNote,
      createProject, viewProject, updateProjectStatus, deleteProject, addNote, handleUpload, handleDrop, getFileIcon, exportProjects,
      clients, showNewClient, editingClient, clientForm, editClient, saveClient, deleteClient, getClientProjects,
      inspirations, inspFilter, filteredInspirations, showNewInspiration, newInsp, createInspiration, deleteInspiration,
      inspTab, onlineInspirations, onlineSources, selectedInspirations, importSingleInspiration, toggleSelectInspiration, selectAllInspirations, batchImportInspirations,
      updateStatus, isUpdating, forceUpdate,
      aiGen, aiStyles, aiHistory, aiMessage, generateImage,
      agents, showNewAgent, editingAgent, agentForm, editAgent, saveAgent, deleteAgent, getAgentColor,
      materials, matFilter, filteredMaterials, showNewMaterial, newMat, createMaterial, deleteMaterial,
      matTab, onlineMatFilter, onlineMaterials, filteredOnlineMaterials, importSingleMaterial,
      customColor, harmonyColors, generateHarmony, copyColor, colorPalettes, copyPalette,
      dimSearch, dimFilter, dimensionData, filteredDimensions,
      priceCalc, styleMultiplier, baseCost, extrasCost, estimatedTotal, toggleExtra,
    };
  }
}).mount('#app');
