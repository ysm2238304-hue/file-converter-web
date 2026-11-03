<template>
  <div class="min-h-screen bg-slate-50 text-slate-800 py-10 px-4 sm:px-6 lg:px-8 font-sans">
    <div class="max-w-4xl mx-auto space-y-8">
      
      <!-- 頂部 Header -->
      <header class="flex items-center justify-between">
        <div class="flex items-center space-x-3">
          <div class="w-10 h-10 rounded-2xl bg-indigo-600 flex items-center justify-center text-white shadow-lg shadow-indigo-500/25 text-lg font-bold">
            📑
          </div>
          <div>
            <h1 class="text-xl font-extrabold tracking-tight text-slate-900">
              DocuMorph <span class="text-xs font-semibold px-2 py-0.5 rounded-full bg-indigo-50 text-indigo-600 border border-indigo-200/60 ml-1">Pro</span>
            </h1>
            <p class="text-xs text-slate-400">現代化檔案轉換工具箱</p>
          </div>
        </div>
        <div class="flex items-center space-x-2 text-xs font-medium text-slate-500 bg-white border border-slate-200 px-3 py-1.5 rounded-full shadow-sm">
          <span class="w-2 h-2 rounded-full bg-emerald-500"></span>
          <span>服務就緒</span>
        </div>
      </header>

      <main class="space-y-6">
        
        <!-- 檔案拖曳艙 -->
        <div 
          @dragover.prevent="isDragging = true"
          @dragleave.prevent="isDragging = false"
          @drop.prevent="handleDrop"
          @click="fileInputRef.click()"
          :class="[
            'border-2 border-dashed rounded-3xl p-8 sm:p-12 text-center cursor-pointer transition-all duration-300',
            isDragging ? 'border-indigo-500 bg-indigo-50/50 scale-[1.01]' : 'border-slate-200 bg-white hover:border-indigo-400/60 shadow-sm'
          ]"
        >
          <input 
            type="file" 
            ref="fileInputRef" 
            multiple 
            class="hidden" 
            accept=".pdf,.docx,.doc,.jpg,.jpeg,.png"
            @change="handleFileInput"
          />
          <div class="flex flex-col items-center justify-center space-y-3">
            <div class="w-14 h-14 rounded-2xl bg-slate-100 flex items-center justify-center text-2xl">
              📤
            </div>
            <div>
              <p class="text-sm font-semibold text-slate-700">
                拖曳檔案至此，或 <span class="text-indigo-600 underline underline-offset-2">瀏覽本機檔案</span>
              </p>
              <p class="text-xs text-slate-400 mt-1">支援 PDF、Word (.docx, .doc)、JPG、PNG</p>
            </div>
          </div>
        </div>

        <!-- 已加入檔案隊列 (支援排序) -->
        <div v-if="uploadedFiles.length > 0" class="space-y-3">
          <div class="flex justify-between items-center px-1">
            <h2 class="text-xs font-bold tracking-wider text-slate-400 uppercase">
              待處理檔案 ({{ uploadedFiles.length }})
            </h2>
            <button @click="clearAll" class="text-xs text-slate-400 hover:text-rose-500">清空全部</button>
          </div>

          <div class="space-y-2">
            <div 
              v-for="(item, index) in uploadedFiles" 
              :key="item.id"
              class="flex items-center justify-between p-3.5 bg-white border border-slate-200/80 rounded-2xl shadow-sm"
            >
              <div class="flex items-center space-x-3 truncate min-w-0">
                <span :class="['px-2 py-1 text-[11px] font-bold rounded-lg uppercase', getBadgeClass(item.ext)]">
                  {{ item.ext }}
                </span>
                <div class="truncate">
                  <p class="text-sm font-semibold text-slate-800 truncate">{{ item.name }}</p>
                  <p class="text-[11px] text-slate-400">
                    {{ formatSize(item.size) }}
                    <span v-if="item.pages" class="ml-2 font-medium text-indigo-600">{{ item.pages }} 頁</span>
                  </p>
                </div>
              </div>

              <!-- 排序與刪除 -->
              <div class="flex items-center space-x-1">
                <button 
                  v-if="index > 0" 
                  @click="moveFile(index, -1)" 
                  class="p-1.5 text-slate-400 hover:bg-slate-100 rounded-lg text-xs"
                >⬆️</button>
                <button 
                  v-if="index < uploadedFiles.length - 1" 
                  @click="moveFile(index, 1)" 
                  class="p-1.5 text-slate-400 hover:bg-slate-100 rounded-lg text-xs"
                >⬇️</button>
                <button 
                  @click="removeFile(index)" 
                  class="p-1.5 text-slate-300 hover:text-rose-500 hover:bg-rose-50 rounded-lg text-xs ml-1"
                >✕</button>
              </div>
            </div>
          </div>
        </div>

        <!-- 轉換模式選單 -->
        <div v-if="uploadedFiles.length > 0" class="space-y-3">
          <h2 class="text-xs font-bold tracking-wider text-slate-400 uppercase px-1">選擇轉換方式</h2>
          <div class="grid grid-cols-2 sm:grid-cols-3 gap-3">
            <div 
              v-for="m in modes" 
              :key="m.id"
              @click="currentMode = m.id"
              :class="[
                'p-4 rounded-2xl border cursor-pointer transition-all text-left',
                currentMode === m.id ? 'border-indigo-600 bg-white ring-2 ring-indigo-600/20 shadow-sm' : 'border-slate-200 bg-white hover:border-slate-300'
              ]"
            >
              <div class="text-2xl mb-1">{{ m.icon }}</div>
              <p class="text-sm font-bold text-slate-800">{{ m.title }}</p>
              <p class="text-xs text-slate-400 mt-0.5">{{ m.desc }}</p>
            </div>
          </div>
        </div>

        <!-- PDF 拆分參數配置 -->
        <div v-if="currentMode === 'split_pdf' && uploadedFiles.length > 0" class="p-5 bg-white border border-slate-200 rounded-2xl space-y-4">
          <h3 class="text-sm font-bold text-slate-700">✂️ 拆分參數</h3>
          <div class="grid grid-cols-3 p-1 bg-slate-100 rounded-xl text-xs font-semibold">
            <button 
              v-for="s in splitOptions" 
              :key="s.id"
              @click="splitSetting.mode = s.id"
              :class="['py-2 rounded-lg transition-all', splitSetting.mode === s.id ? 'bg-white text-slate-800 shadow-sm' : 'text-slate-500']"
            >
              {{ s.title }}
            </button>
          </div>

          <div v-if="splitSetting.mode === 'ranges'" class="space-y-1">
            <label class="text-xs text-slate-500">頁碼範圍 (以逗號或連字號分隔)</label>
            <input 
              v-model="splitSetting.rangesStr" 
              type="text" 
              placeholder="例: 1-3, 5, 8-10" 
              class="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500/20"
            />
          </div>

          <div v-if="splitSetting.mode === 'fixed_count'" class="flex items-center space-x-2 text-sm text-slate-600">
            <span>每</span>
            <input 
              v-model.number="splitSetting.chunkSize" 
              type="number" 
              min="1" 
              class="w-20 px-3 py-1.5 text-center bg-slate-50 border border-slate-200 rounded-xl font-bold"
            />
            <span>頁拆為一份</span>
          </div>
        </div>

        <!-- 執行按鈕 -->
        <div v-if="uploadedFiles.length > 0">
          <button 
            @click="submitConversion" 
            :disabled="isProcessing"
            class="w-full py-4 rounded-2xl bg-indigo-600 hover:bg-indigo-700 text-white font-bold shadow-lg shadow-indigo-500/25 transition-all disabled:opacity-50"
          >
            {{ isProcessing ? '轉檔處理中...' : '開始轉換作業' }}
          </button>
        </div>

        <!-- 進度條 -->
        <div v-if="isProcessing || resultDownloadUrl" class="p-5 bg-white border border-slate-200 rounded-2xl space-y-3">
          <div class="flex justify-between text-xs text-slate-500">
            <span>{{ statusMessage }}</span>
            <span class="font-bold text-indigo-600">{{ progress }}%</span>
          </div>
          <div class="w-full bg-slate-100 h-2 rounded-full overflow-hidden">
            <div class="bg-indigo-600 h-full transition-all duration-300" :style="{ width: `${progress}%` }"></div>
          </div>
        </div>

        <!-- 成功下載卡片 -->
        <div v-if="resultDownloadUrl" class="p-6 bg-emerald-50 border border-emerald-200 rounded-2xl flex items-center justify-between">
          <div>
            <p class="text-sm font-bold text-emerald-900">轉換作業完成！</p>
            <p class="text-xs text-emerald-700 mt-0.5">檔案已就緒，請點擊右側按鈕儲存</p>
          </div>
          <a 
            :href="resultDownloadUrl" 
            :download="resultFilename"
            class="px-5 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold rounded-xl shadow transition-all"
          >
            下載檔案 ({{ resultFilename }})
          </a>
        </div>

      </main>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';

const fileInputRef = ref(null);
const isDragging = ref(false);
const uploadedFiles = ref([]);
const currentMode = ref('merge_pdf');
const isProcessing = ref(false);
const progress = ref(0);
const statusMessage = ref('就緒');
const resultDownloadUrl = ref('');
const resultFilename = ref('');

const splitSetting = ref({
  mode: 'all_single',
  rangesStr: '',
  chunkSize: 2
});

const splitOptions = [
  { id: 'all_single', title: '全拆為單頁' },
  { id: 'ranges', title: '自訂區間' },
  { id: 'fixed_count', title: '固定分卷' }
];

const modes = [
  { id: 'merge_pdf', title: '合併多份 PDF', icon: '📑', desc: '串接多份文件為一檔' },
  { id: 'split_pdf', title: '拆分 PDF 頁面', icon: '✂️', desc: '提取頁碼或單頁拆解' },
  { id: 'pdf_to_word', title: 'PDF 轉 Word', icon: '📝', desc: '匯出為 .docx 文件' },
  { id: 'pdf_to_jpg', title: 'PDF 轉圖片', icon: '🖼️', desc: '高清晰 JPG 圖檔' },
  { id: 'word_to_pdf', title: 'Word 轉 PDF', icon: '📄', desc: '無損固定文件排版' },
  { id: 'jpg_to_pdf', title: '圖片轉 PDF', icon: '🖼️', desc: '多張圖檔合併轉出' }
];

const handleFileInput = (e) => {
  addFiles(e.target.files);
  e.target.value = '';
};

const handleDrop = (e) => {
  isDragging.value = false;
  addFiles(e.dataTransfer.files);
};

const addFiles = async (fileList) => {
  for (let f of fileList) {
    const ext = f.name.split('.').pop().toLowerCase();
    const item = {
      id: Math.random().toString(36).substring(2, 9),
      name: f.name,
      size: f.size,
      ext: ext,
      rawFile: f,
      pages: null
    };
    uploadedFiles.value.push(item);

    if (ext === 'pdf') {
      const formData = new FormData();
      formData.append('file', f);
      try {
        const res = await fetch('/api/info/pdf', { method: 'POST', body: formData });
        const data = await res.json();
        if (!data.encrypted) {
          item.pages = data.pages;
        }
      } catch (err) {
        console.error("無法取得頁數", err);
      }
    }
  }

  if (uploadedFiles.value.length > 1) {
    currentMode.value = 'merge_pdf';
  } else if (uploadedFiles.value.length === 1) {
    const ext = uploadedFiles.value[0].ext;
    if (ext === 'docx' || ext === 'doc') currentMode.value = 'word_to_pdf';
    else if (ext === 'pdf') currentMode.value = 'pdf_to_word';
  }
};

const moveFile = (index, offset) => {
  const target = index + offset;
  const item = uploadedFiles.value.splice(index, 1)[0];
  uploadedFiles.value.splice(target, 0, item);
};

const removeFile = (index) => uploadedFiles.value.splice(index, 1);
const clearAll = () => {
  uploadedFiles.value = [];
  resultDownloadUrl.value = '';
  isProcessing.value = false;
};

const getBadgeClass = (ext) => {
  switch (ext) {
    case 'pdf': return 'bg-rose-50 text-rose-600';
    case 'docx':
    case 'doc': return 'bg-blue-50 text-blue-600';
    default: return 'bg-emerald-50 text-emerald-600';
  }
};

const formatSize = (b) => {
  if (b < 1048576) return (b / 1024).toFixed(1) + ' KB';
  return (b / 1048576).toFixed(1) + ' MB';
};

const submitConversion = async () => {
  isProcessing.value = true;
  resultDownloadUrl.value = '';
  progress.value = 15;
  statusMessage.value = '正在上傳檔案至轉檔引擎...';

  const formData = new FormData();
  uploadedFiles.value.forEach(item => {
    formData.append('files', item.rawFile);
  });

  formData.append('mode', currentMode.value);
  if (currentMode.value === 'split_pdf') {
    formData.append('split_mode', splitSetting.value.mode);
    formData.append('ranges_str', splitSetting.value.rangesStr);
    formData.append('chunk_size', splitSetting.value.chunkSize);
  }

  try {
    progress.value = 45;
    statusMessage.value = '檔案處理與轉換計算中...';

    const response = await fetch('/api/convert', {
      method: 'POST',
      body: formData
    });

    if (!response.ok) {
      const err = await response.json();
      throw new Error(err.detail || '轉檔過程發生未預期錯誤');
    }

    const data = await response.json();
    progress.value = 100;
    statusMessage.value = '處理完成！';
    resultDownloadUrl.value = data.download_url;
    resultFilename.value = data.filename;
  } catch (error) {
    alert(`轉檔失敗: ${error.message}`);
  } finally {
    isProcessing.value = false;
  }
};
</script>
