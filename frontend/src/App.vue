<template>
  <!-- 確保根容器滿版，並讓背景點點延伸至整個螢幕 -->
  <div class="min-h-screen w-full bg-[#FFF9E6] bg-dots text-[#2C3E50] font-cartoon antialiased flex flex-col relative selection:bg-[#FF6B6B] selection:text-white">
    
    <!-- ================= 1. 卡通風格頂部導航列 ================= -->
    <header class="bg-white border-b-[3px] border-[#2C3E50] sticky top-0 z-50">
      <div class="max-w-[1440px] mx-auto px-4 sm:px-8 h-20 flex items-center justify-between">
        
        <!-- 左側 Logo 與主要功能 -->
        <div class="flex items-center space-x-8">
          <!-- 卡通風格 LOGO -->
          <div @click="goToHome" class="flex items-center space-x-2 cursor-pointer select-none group">
            <span class="bg-[#FF6B6B] text-white px-3 py-1.5 rounded-xl border-[3px] border-[#2C3E50] shadow-[3px_3px_0px_#2C3E50] rotate-[-5deg] text-xl font-black group-hover:rotate-0 transition-transform">
              PDF
            </span>
            <span class="text-2xl font-black tracking-tight text-[#2C3E50]">黑糖饅頭 🥟</span>
          </div>

          <!-- 頂部捷徑連結 -->
          <nav class="hidden md:flex items-center space-x-6 text-[15px] font-black text-[#2C3E50]">
            <button @click="selectTool('merge_pdf')" class="hover:text-[#FF6B6B] transition-colors cursor-pointer">合併PDF</button>
            <button @click="selectTool('split_pdf')" class="hover:text-[#FF6B6B] transition-colors cursor-pointer">拆分PDF</button>
            <button @click="selectTool('pdf_to_word')" class="hover:text-[#FF6B6B] transition-colors cursor-pointer">PDF 轉換 ▾</button>
            <button @click="goToHome" class="hover:text-[#FF6B6B] transition-colors cursor-pointer">所有 PDF 工具 ▾</button>
          </nav>
        </div>

        <!-- 右側操作按鈕：問題回報 -->
        <div class="flex items-center">
          <button 
            @click="openFeedbackModal" 
            class="cartoon-btn px-5 py-2 sm:px-6 sm:py-2.5 rounded-xl bg-[#FECA57] border-[3px] border-[#2C3E50] shadow-[4px_4px_0px_#2C3E50] text-[#2C3E50] text-sm sm:text-[15px] font-black flex items-center gap-1.5 cursor-pointer"
          >
            <span>💬</span>
            <span>問題回報</span>
          </button>
        </div>
      </div>
    </header>

    <!-- ================= 2. 主內容區域 ================= -->
    <main class="flex-1 flex flex-col relative w-full overflow-hidden">
      
      <!-- 背景裝飾漂浮物 -->
      <div class="absolute top-20 left-10 text-5xl animate-bounce hidden lg:block opacity-50 z-0">✨</div>
      <div class="absolute top-40 right-20 text-6xl animate-pulse hidden lg:block opacity-50 z-0">🚀</div>

      <!-- ================= 視圖 1：首頁 6 欄矩陣大廳 ================= -->
      <section v-if="currentStep === 'hub'" class="max-w-[1440px] mx-auto px-4 sm:px-8 py-10 w-full space-y-10 relative z-10">
        
        <!-- 標題區域 -->
        <div class="text-center space-y-4 max-w-4xl mx-auto pt-4">
          <h1 class="text-4xl sm:text-6xl font-black text-[#2C3E50] tracking-tight leading-tight">
            <span class="relative inline-block">
              <span class="relative z-10 px-2">黑糖饅頭很好吃</span>
              <span class="absolute bottom-2 left-0 w-full h-4 sm:h-6 bg-[#FECA57] -rotate-2 rounded-lg border-[2px] border-[#2C3E50] -z-0"></span>
            </span>
            🥟
          </h1>
          <p class="text-base sm:text-lg font-bold text-gray-500 leading-relaxed max-w-2xl mx-auto pt-2">
            完全免費、超直覺！把你搞不定的 PDF 檔案交給我們，就像吃饅頭一樣簡單又快速 ✨
          </p>
        </div>

        <!-- 分類切換膠囊列 -->
        <div class="flex items-center justify-center flex-wrap gap-3 pt-4">
          <button 
            v-for="cat in categories" 
            :key="cat.id"
            @click="activeCategory = cat.id"
            :class="[
              'px-5 py-2 rounded-full text-sm font-black border-[3px] transition-all duration-200 cursor-pointer',
              activeCategory === cat.id 
                ? 'bg-[#FF6B6B] text-white border-[#2C3E50] shadow-[3px_3px_0px_#2C3E50] -rotate-2 scale-105' 
                : 'bg-white text-[#2C3E50] border-[#2C3E50] shadow-[2px_2px_0px_#2C3E50] hover:-translate-y-0.5 hover:shadow-[4px_4px_0px_#2C3E50]'
            ]"
          >
            {{ cat.name }}
          </button>
        </div>

        <!-- 6 欄式卡通卡片網格 -->
        <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-5 pt-4">
          <div 
            v-for="tool in filteredTools" 
            :key="tool.id"
            @click="onCardClick(tool)"
            :class="[
              'group bg-white rounded-3xl border-[3px] border-[#2C3E50] p-4 flex flex-col justify-between transition-all duration-200 relative select-none',
              tool.enabled 
                ? 'cartoon-card shadow-[5px_5px_0px_#2C3E50] cursor-pointer hover:bg-[#FFF9E6]' 
                : 'opacity-70 cursor-not-allowed shadow-[3px_3px_0px_#A0AAB5] border-[#A0AAB5]'
            ]"
          >
            <!-- 即將推出角標 -->
            <div v-if="!tool.enabled" class="absolute -top-3 -right-3 bg-[#FECA57] border-[2px] border-[#2C3E50] text-[10px] font-black px-2 py-1 rounded-full rotate-12 shadow-[2px_2px_0px_#2C3E50] z-10">
              即將推出 🚧
            </div>

            <!-- 頂部 App 圖章圖示 -->
            <div class="space-y-4">
              <div :class="['w-12 h-12 rounded-2xl flex items-center justify-center text-white border-[3px] border-[#2C3E50] shadow-[2px_2px_0px_#2C3E50] transition-transform group-hover:scale-110 group-hover:-rotate-6', tool.iconBg]">
                <component :is="tool.iconSvg" />
              </div>

              <!-- 卡片標題與描述 -->
              <div class="space-y-1.5">
                <h3 class="text-base font-black text-[#2C3E50] leading-snug">
                  {{ tool.title }}
                </h3>
                <p class="text-[12px] font-bold text-gray-500 leading-relaxed line-clamp-3">
                  {{ tool.desc }}
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- ================= 視圖 2：獨立工具工作台 (Workspace) ================= -->
      <section v-else-if="currentStep === 'workspace'" class="flex-1 flex flex-col relative z-10">
        
        <!-- 頂部次級工具列 -->
        <div class="bg-white border-b-[3px] border-[#2C3E50] py-4 px-6 flex items-center justify-between shadow-sm">
          <button @click="goToHome" class="text-sm font-black text-[#2C3E50] hover:text-[#FF6B6B] flex items-center space-x-2 bg-[#F0F4F8] px-4 py-2 rounded-xl border-[2px] border-[#2C3E50] shadow-[2px_2px_0px_#2C3E50] cartoon-btn cursor-pointer">
            <span>← 返回大廳</span>
          </button>
          <div class="text-xl font-black text-[#2C3E50] flex items-center gap-2">
            {{ activeToolMeta.title }} 🛠️
          </div>
          <button @click="clearWorkspace" class="text-sm font-black text-slate-400 hover:text-[#FF6B6B] cursor-pointer">
            清空已選
          </button>
        </div>

        <!-- 尚未選擇檔案：巨型卡通上傳區 -->
        <div v-if="files.length === 0" class="flex-1 flex items-center justify-center p-6 min-h-[60vh]">
          <div 
            @dragover.prevent="isDragging = true"
            @dragleave.prevent="isDragging = false"
            @drop.prevent="handleDrop"
            :class="[
              'max-w-2xl w-full p-12 text-center rounded-[2rem] border-[4px] border-dashed transition-all duration-300 flex flex-col items-center justify-center space-y-8 bg-white',
              isDragging ? 'border-[#FF6B6B] bg-[#FFF0F0] scale-105 shadow-[8px_8px_0px_#FF6B6B]' : 'border-[#2C3E50] shadow-[8px_8px_0px_#2C3E50]'
            ]"
          >
            <input 
              type="file" 
              ref="fileInputRef" 
              multiple 
              class="hidden" 
              :accept="activeToolMeta.accept"
              @change="handleFileInput" 
            />

            <div class="text-7xl animate-bounce">📂</div>
            
            <div class="space-y-3">
              <h2 class="text-3xl font-black text-[#2C3E50]">{{ activeToolMeta.title }}</h2>
              <p class="text-sm font-bold text-gray-500">{{ activeToolMeta.desc }}</p>
            </div>

            <button 
              @click="triggerFileInput"
              class="cartoon-btn px-12 py-5 rounded-2xl bg-[#48DBFB] text-[#2C3E50] border-[4px] border-[#2C3E50] shadow-[6px_6px_0px_#2C3E50] font-black text-xl transition-all cursor-pointer"
            >
              {{ activeToolMeta.buttonText }}
            </button>

            <p class="text-sm font-bold text-gray-400">或將檔案直接拖放至此 ✨</p>
          </div>
        </div>

        <!-- 已選擇檔案區塊 -->
        <div v-else class="flex-1 max-w-[1440px] w-full mx-auto p-4 sm:p-8 grid grid-cols-1 lg:grid-cols-4 gap-8 items-start">
          
          <!-- ================= 左側區域 ================= -->
          <div class="lg:col-span-3 space-y-5">
            
            <!-- 情況 A：拆分 PDF 模式（顯示全部頁面縮圖矩陣視覺化選取） -->
            <div v-if="currentToolId === 'split_pdf'" class="space-y-5">
              <!-- 文件基本資訊與快捷選取列 -->
              <div class="flex flex-wrap items-center justify-between gap-3 bg-white p-4 rounded-2xl border-[3px] border-[#2C3E50] shadow-[4px_4px_0px_#2C3E50]">
                <div class="flex items-center gap-2">
                  <span class="text-sm font-black text-[#2C3E50]">
                    📄 {{ files[0]?.name }} (共 {{ splitPages.length }} 頁)
                  </span>
                  <span v-if="isRenderingPages" class="text-xs font-bold text-[#FF6B6B] animate-pulse">
                    縮圖生成中... ⏳
                  </span>
                </div>

                <!-- 快捷勾選按鈕組 -->
                <div class="flex items-center gap-2">
                  <button @click="selectAllPages" class="px-2.5 py-1 text-xs font-black bg-[#F0F4F8] hover:bg-[#FECA57] border-[2px] border-[#2C3E50] rounded-lg shadow-[1px_1px_0px_#2C3E50] transition-colors cursor-pointer">全選</button>
                  <button @click="clearAllPages" class="px-2.5 py-1 text-xs font-black bg-[#F0F4F8] hover:bg-[#FF6B6B] hover:text-white border-[2px] border-[#2C3E50] rounded-lg shadow-[1px_1px_0px_#2C3E50] transition-colors cursor-pointer">清空</button>
                  <button @click="selectOddPages" class="px-2.5 py-1 text-xs font-black bg-[#F0F4F8] hover:bg-[#FECA57] border-[2px] border-[#2C3E50] rounded-lg shadow-[1px_1px_0px_#2C3E50] transition-colors cursor-pointer">奇數頁</button>
                  <button @click="selectEvenPages" class="px-2.5 py-1 text-xs font-black bg-[#F0F4F8] hover:bg-[#FECA57] border-[2px] border-[#2C3E50] rounded-lg shadow-[1px_1px_0px_#2C3E50] transition-colors cursor-pointer">偶數頁</button>
                  <button @click="triggerFileInput" class="text-xs font-black text-[#FF6B6B] bg-[#FFF0F0] px-3 py-1 rounded-lg border-[2px] border-[#FF6B6B] cursor-pointer">更換檔案</button>
                </div>
              </div>

              <!-- 頁面縮圖矩陣 Grid -->
              <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 xl:grid-cols-5 gap-4">
                <div 
                  v-for="page in splitPages" 
                  :key="page.pageNum"
                  @click="togglePageSelection(page.pageNum)"
                  :class="[
                    'group bg-white rounded-2xl border-[3px] p-2 relative flex flex-col justify-between aspect-[3/4] cursor-pointer transition-all duration-150 select-none',
                    selectedPages.has(page.pageNum) 
                      ? 'border-[#FF6B6B] bg-[#FFF8F8] shadow-[5px_5px_0px_#FF6B6B] -translate-y-1' 
                      : 'border-[#2C3E50] shadow-[3px_3px_0px_#2C3E50] opacity-80 hover:opacity-100 hover:shadow-[5px_5px_0px_#2C3E50]'
                  ]"
                >
                  <!-- 頁碼標籤 (左上) -->
                  <div class="absolute top-2.5 left-2.5 w-7 h-7 rounded-full bg-[#FECA57] border-[2px] border-[#2C3E50] text-[#2C3E50] text-xs font-black flex items-center justify-center shadow-[1px_1px_0px_#2C3E50] z-10">
                    {{ page.pageNum }}
                  </div>

                  <!-- 選取狀態勾勾 (右上) -->
                  <div 
                    v-if="selectedPages.has(page.pageNum)"
                    class="absolute top-2.5 right-2.5 w-7 h-7 rounded-full bg-[#1DD1A1] border-[2px] border-[#2C3E50] text-white text-xs font-black flex items-center justify-center shadow-[1px_1px_0px_#2C3E50] z-10 animate-bounce"
                  >
                    ✓
                  </div>

                  <!-- 頁面縮圖顯示 -->
                  <div class="flex-1 flex items-center justify-center overflow-hidden rounded-xl border-[2px] border-slate-200 bg-[#F9FAFB] my-1 p-1">
                    <img 
                      v-if="page.thumbnail" 
                      :src="page.thumbnail" 
                      class="max-w-full max-h-full object-contain pointer-events-none drop-shadow-sm" 
                    />
                    <div v-else class="text-xs font-bold text-gray-300 flex flex-col items-center gap-1">
                      <span class="animate-spin text-lg">⏳</span>
                      <span>加載中</span>
                    </div>
                  </div>

                  <!-- 底部提示文字 -->
                  <div class="text-center text-[11px] font-black" :class="selectedPages.has(page.pageNum) ? 'text-[#FF6B6B]' : 'text-gray-400'">
                    {{ selectedPages.has(page.pageNum) ? '已選取' : '點擊加入' }}
                  </div>
                </div>
              </div>
            </div>

            <!-- 情況 B：合併 PDF 與其他功能（文件列表 + 封面第 1 頁縮圖） -->
            <div v-else class="space-y-5">
              <div class="flex items-center justify-between bg-white p-4 rounded-2xl border-[3px] border-[#2C3E50] shadow-[4px_4px_0px_#2C3E50]">
                <span class="text-sm font-black text-[#2C3E50]">
                  已選取 {{ files.length }} 個檔案（可按箭頭調換合併順序）
                </span>
                <button @click="triggerFileInput" class="text-sm font-black text-[#FF6B6B] hover:underline bg-[#FFF0F0] px-3 py-1 rounded-lg border-[2px] border-[#FF6B6B] cursor-pointer">
                  ➕ 新增檔案
                </button>
              </div>

              <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-5">
                <div 
                  v-for="(item, index) in files" 
                  :key="item.id"
                  class="group bg-white rounded-2xl border-[3px] border-[#2C3E50] shadow-[4px_4px_0px_#2C3E50] p-3 relative flex flex-col justify-between aspect-[3/4] hover:-translate-y-1 transition-transform"
                >
                  <!-- 順序標籤 -->
                  <div class="absolute top-3 left-3 w-7 h-7 rounded-full bg-[#FECA57] border-[2px] border-[#2C3E50] text-[#2C3E50] text-xs font-black flex items-center justify-center shadow-[1px_1px_0px_#2C3E50] z-10">
                    {{ index + 1 }}
                  </div>

                  <!-- 刪除按鈕 -->
                  <button 
                    @click="removeFile(index)"
                    class="absolute top-3 right-3 w-7 h-7 rounded-full bg-white border-[2px] border-[#2C3E50] text-[#2C3E50] hover:bg-[#FF6B6B] hover:text-white flex items-center justify-center text-xs transition-colors shadow-[1px_1px_0px_#2C3E50] z-10 cursor-pointer"
                  >
                    ✕
                  </button>

                  <!-- 封面縮圖預覽 -->
                  <div class="flex-1 flex flex-col items-center justify-center pt-2 overflow-hidden">
                    <div class="w-20 h-28 bg-[#F0F4F8] border-[2px] border-[#2C3E50] rounded-xl flex items-center justify-center shadow-[2px_2px_0px_#2C3E50] overflow-hidden p-1">
                      <img 
                        v-if="item.thumbnail" 
                        :src="item.thumbnail" 
                        class="max-w-full max-h-full object-contain rounded" 
                      />
                      <span v-else class="text-sm font-black uppercase tracking-wider text-[#FF6B6B]">
                        {{ item.ext }}
                      </span>
                    </div>

                    <p class="text-sm font-black text-[#2C3E50] truncate w-full text-center mt-2 px-1">
                      {{ item.name }}
                    </p>
                    <p class="text-[11px] font-bold text-gray-400">
                      {{ formatSize(item.size) }}
                      <span v-if="item.pages" class="text-[#FF6B6B] font-black ml-1">({{ item.pages }} 頁)</span>
                    </p>
                  </div>

                  <!-- 排序控制箭頭 -->
                  <div class="flex items-center justify-center space-x-3 pt-2 border-t-[2px] border-slate-100 mt-2">
                    <button :disabled="index === 0" @click="moveFile(index, -1)" class="p-1 text-sm text-[#2C3E50] hover:text-[#FF6B6B] disabled:opacity-20 font-black cursor-pointer">◀</button>
                    <span class="text-[10px] text-slate-300 font-black tracking-widest">順序</span>
                    <button :disabled="index === files.length - 1" @click="moveFile(index, 1)" class="p-1 text-sm text-[#2C3E50] hover:text-[#FF6B6B] disabled:opacity-20 font-black cursor-pointer">▶</button>
                  </div>
                </div>
              </div>
            </div>

          </div>

          <!-- ================= 右側控制面版 ================= -->
          <div class="lg:col-span-1 bg-white p-6 rounded-[2rem] border-[3px] border-[#2C3E50] shadow-[6px_6px_0px_#2C3E50] space-y-6 sticky top-24">
            <div class="space-y-1">
              <h3 class="text-xl font-black text-[#2C3E50]">{{ activeToolMeta.title }}</h3>
              <p class="text-xs font-bold text-gray-400">配置你的專屬饅頭配方 ⚙️</p>
            </div>

            <!-- 拆分設定選項 -->
            <div v-if="currentToolId === 'split_pdf'" class="space-y-4 pt-4 border-t-[2px] border-slate-100">
              <label class="text-sm font-black text-[#2C3E50] block">分割模式</label>
              <div class="space-y-3 text-sm font-bold text-gray-600">
                <label class="flex items-center space-x-3 cursor-pointer">
                  <input type="radio" value="ranges" v-model="splitParams.mode" class="w-4 h-4 text-[#FF6B6B] focus:ring-[#FF6B6B] border-[#2C3E50]">
                  <span>自選頁面 / 指定範圍 (點左側縮圖)</span>
                </label>
                <label class="flex items-center space-x-3 cursor-pointer">
                  <input type="radio" value="all_single" v-model="splitParams.mode" class="w-4 h-4 text-[#FF6B6B] focus:ring-[#FF6B6B] border-[#2C3E50]">
                  <span>全部分割為獨立單頁</span>
                </label>
                
                <div v-if="splitParams.mode === 'ranges'" class="space-y-1 pt-1">
                  <input 
                    v-model="splitParams.rangesStr" 
                    @input="onRangesInput"
                    type="text" 
                    placeholder="例如: 1-3, 5, 8-10" 
                    class="w-full px-4 py-2 text-sm font-bold bg-[#F0F4F8] border-[2px] border-[#2C3E50] rounded-xl focus:outline-none focus:ring-2 focus:ring-[#FF6B6B] shadow-[inset_2px_2px_0px_rgba(0,0,0,0.05)]" 
                  />
                  <p class="text-[11px] font-bold text-gray-400">已勾選 {{ selectedPages.size }} 頁，輸入範圍會自動連動！</p>
                </div>
              </div>
            </div>

            <div class="bg-[#FFF9E6] p-4 rounded-xl border-[2px] border-[#2C3E50] shadow-[inset_2px_2px_0px_rgba(0,0,0,0.05)] text-sm space-y-2 font-bold text-gray-500">
              <div class="flex justify-between">
                <span>檔案數量:</span>
                <span class="font-black text-[#2C3E50]">{{ files.length }} 個</span>
              </div>
              <div class="flex justify-between">
                <span>合計大小:</span>
                <span class="font-black text-[#2C3E50]">{{ formatSize(totalBytes) }}</span>
              </div>
            </div>

            <button @click="executeTool" :disabled="isProcessing" class="cartoon-btn w-full py-4 rounded-2xl bg-[#FF6B6B] text-white border-[3px] border-[#2C3E50] shadow-[4px_4px_0px_#2C3E50] font-black text-lg transition-all flex items-center justify-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer">
              <span>{{ isProcessing ? '饅頭加熱中... ♨️' : activeToolMeta.actionText }}</span>
            </button>

            <div v-if="isProcessing" class="space-y-2">
              <div class="w-full bg-[#F0F4F8] h-4 rounded-full border-[2px] border-[#2C3E50] overflow-hidden p-0.5">
                <div class="bg-[#1DD1A1] h-full rounded-full transition-all duration-300 border-r-[2px] border-[#2C3E50]" :style="{ width: `${progress}%` }"></div>
              </div>
              <p class="text-xs text-center font-black text-[#2C3E50]">{{ progressText }}</p>
            </div>
          </div>
        </div>
      </section>

      <!-- ================= 視圖 3：沉浸式成果下載頁 ================= -->
      <section v-else-if="currentStep === 'success'" class="flex-1 flex items-center justify-center p-6 relative z-10 min-h-[60vh]">
        <div class="max-w-md w-full bg-white p-10 rounded-[2rem] border-[4px] border-[#2C3E50] shadow-[8px_8px_0px_#2C3E50] text-center space-y-8">
          <div class="w-20 h-20 bg-[#1DD1A1] text-white rounded-2xl flex items-center justify-center text-4xl mx-auto font-black border-[4px] border-[#2C3E50] shadow-[4px_4px_0px_#2C3E50] rotate-6 animate-pulse">
            ✓
          </div>

          <div class="space-y-2">
            <h2 class="text-3xl font-black text-[#2C3E50]">饅頭出爐囉！ 🥟</h2>
            <p class="text-sm font-bold text-gray-400">輸出檔案：{{ downloadFilename }}</p>
          </div>

          <a :href="downloadUrl" :download="downloadFilename" class="cartoon-btn block w-full py-5 rounded-2xl bg-[#FECA57] text-[#2C3E50] border-[3px] border-[#2C3E50] shadow-[4px_4px_0px_#2C3E50] font-black text-lg transition-all cursor-pointer">
            📥 立即下載檔案
          </a>

          <div class="pt-4 flex items-center justify-between text-xs font-bold text-gray-400 border-t-[2px] border-slate-100">
            <button @click="goToHome" class="hover:text-[#FF6B6B] font-black transition-colors cursor-pointer">
              ← 返回處理其他文件
            </button>
            <span class="flex items-center gap-1">🔥 暫存 30 分鐘後自動銷毀</span>
          </div>
        </div>
      </section>

    </main>

    <!-- ================= 3. 問題回報彈窗 (直寄 Gmail) ================= -->
    <div 
      v-if="showFeedbackModal" 
      class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-xs"
      @click.self="closeFeedbackModal"
    >
      <div class="bg-white w-full max-w-md rounded-[2rem] border-[4px] border-[#2C3E50] shadow-[8px_8px_0px_#2C3E50] p-6 sm:p-8 space-y-5 relative select-none">
        
        <!-- 右上角關閉按鈕 -->
        <button 
          @click="closeFeedbackModal"
          class="absolute top-5 right-5 w-8 h-8 rounded-full bg-white border-[2px] border-[#2C3E50] text-[#2C3E50] hover:bg-[#FF6B6B] hover:text-white flex items-center justify-center text-sm font-black transition-colors shadow-[2px_2px_0px_#2C3E50] cursor-pointer"
        >
          ✕
        </button>

        <!-- 彈窗標題 -->
        <div class="space-y-1">
          <div class="flex items-center gap-2">
            <span class="text-2xl">📮</span>
            <h3 class="text-2xl font-black text-[#2C3E50]">問題回報與建議</h3>
          </div>
          <p class="text-xs font-bold text-gray-400">有任何 Bug 或轉檔問題？送出後會直接寄到作者信箱！</p>
        </div>

        <!-- 回報表單 -->
        <form @submit.prevent="submitFeedback" class="space-y-4 pt-1">
          <div class="space-y-1">
            <label class="text-xs font-black text-[#2C3E50] block">您的 Email <span class="text-gray-400 font-bold">(選填，若需回覆請填)</span></label>
            <input 
              v-model="feedbackForm.email"
              type="email" 
              placeholder="example@gmail.com"
              class="w-full px-3.5 py-2 text-sm font-bold bg-[#F0F4F8] border-[2px] border-[#2C3E50] rounded-xl focus:outline-none focus:ring-2 focus:ring-[#FECA57] shadow-[inset_2px_2px_0px_rgba(0,0,0,0.05)]"
            />
          </div>

          <div class="space-y-1">
            <label class="text-xs font-black text-[#2C3E50] block">問題類型</label>
            <select 
              v-model="feedbackForm.type"
              class="w-full px-3.5 py-2 text-sm font-bold bg-[#F0F4F8] border-[2px] border-[#2C3E50] rounded-xl focus:outline-none focus:ring-2 focus:ring-[#FECA57] shadow-[inset_2px_2px_0px_rgba(0,0,0,0.05)]"
            >
              <option value="轉檔失敗">❌ 轉檔失敗 / 報錯</option>
              <option value="格式排版跑掉">📑 格式排版跑掉</option>
              <option value="功能建議">💡 新功能建議</option>
              <option value="其他">💬 其他問題</option>
            </select>
          </div>

          <div class="space-y-1">
            <label class="text-xs font-black text-[#2C3E50] block">詳細說明 <span class="text-[#FF6B6B]">*</span></label>
            <textarea 
              v-model="feedbackForm.message"
              required
              rows="3"
              placeholder="請簡單描述狀況（例如：轉 Word 時排版跑掉、上傳某個檔案時卡住...）"
              class="w-full px-3.5 py-2 text-sm font-bold bg-[#F0F4F8] border-[2px] border-[#2C3E50] rounded-xl focus:outline-none focus:ring-2 focus:ring-[#FECA57] shadow-[inset_2px_2px_0px_rgba(0,0,0,0.05)] resize-none"
            ></textarea>
          </div>

          <button 
            type="submit" 
            :disabled="isSubmittingFeedback"
            class="cartoon-btn w-full py-3.5 rounded-xl bg-[#1DD1A1] text-white border-[3px] border-[#2C3E50] shadow-[3px_3px_0px_#2C3E50] font-black text-base transition-all flex items-center justify-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
          >
            <span>{{ isSubmittingFeedback ? '正在把信件送出... ✉️' : '確認送出 🚀' }}</span>
          </button>

          <p v-if="feedbackStatusMsg" :class="['text-xs text-center font-black pt-1', feedbackStatusType === 'success' ? 'text-[#1DD1A1]' : 'text-[#FF6B6B]']">
            {{ feedbackStatusMsg }}
          </p>
        </form>
      </div>
    </div>

    <!-- 頁尾 -->
    <footer class="py-8 text-center text-sm font-black text-gray-400 relative z-10">
      © 黑糖饅頭很好吃 · 100% 免費且易於使用的線上 PDF 工具 🥟
    </footer>

  </div>
</template>

<script setup>
import { ref, computed, h } from 'vue';
import * as pdfjsLib from 'pdfjs-dist';

// 指定 PDF.js worker 路徑 (採用官方 CDN，保證打包零報錯)
pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';

// 狀態控制
const currentStep = ref('hub');
const currentToolId = ref('merge_pdf');
const activeCategory = ref('all');
const isDragging = ref(false);
const fileInputRef = ref(null);

const files = ref([]);
const isProcessing = ref(false);
const progress = ref(0);
const progressText = ref('');
const downloadUrl = ref('');
const downloadFilename = ref('');

// ================= 拆分預覽與頁面選取狀態 =================
const splitPages = ref([]);            // 儲存拆分文件的每一頁縮圖 [{ pageNum, thumbnail }]
const selectedPages = ref(new Set());  // 儲存被使用者選取的頁碼
const isRenderingPages = ref(false);

const splitParams = ref({
  mode: 'ranges',
  rangesStr: '1',
  chunkSize: 2
});

// ================= 問題回報彈窗狀態 =================
const showFeedbackModal = ref(false);
const isSubmittingFeedback = ref(false);
const feedbackStatusMsg = ref('');
const feedbackStatusType = ref('success');

const feedbackForm = ref({
  email: '',
  type: '轉檔失敗',
  message: ''
});

const FORMSPREE_ENDPOINT = 'https://formspree.io/f/xzeekqlz';

const openFeedbackModal = () => {
  showFeedbackModal.value = true;
  feedbackStatusMsg.value = '';
};

const closeFeedbackModal = () => {
  showFeedbackModal.value = false;
};

const submitFeedback = async () => {
  if (!feedbackForm.value.message.trim()) return;

  isSubmittingFeedback.value = true;
  feedbackStatusMsg.value = '';

  const payload = {
    type: feedbackForm.value.type,
    message: feedbackForm.value.message.trim()
  };
  if (feedbackForm.value.email && feedbackForm.value.email.trim()) {
    payload.email = feedbackForm.value.email.trim();
  }

  try {
    const res = await fetch(FORMSPREE_ENDPOINT, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify(payload)
    });

    if (res.ok) {
      feedbackStatusType.value = 'success';
      feedbackStatusMsg.value = '回報已寄出！作者的 Gmail 已收到通知 🥟';
      feedbackForm.value.message = '';
      feedbackForm.value.email = '';
      setTimeout(() => {
        closeFeedbackModal();
        feedbackStatusMsg.value = '';
      }, 1800);
    } else {
      throw new Error('傳送失敗');
    }
  } catch (err) {
    feedbackStatusType.value = 'error';
    feedbackStatusMsg.value = '傳送失敗，請確認網路連線或稍後再試！';
  } finally {
    isSubmittingFeedback.value = false;
  }
};

// ================= PDF.js 本機渲染工具函式 =================
// 渲染特定頁面為 Base64 縮圖 (寬度設為 160px 既清晰又節省瀏覽器記憶體)
const renderPageThumbnail = async (pdfDoc, pageNum, targetWidth = 160) => {
  try {
    const page = await pdfDoc.getPage(pageNum);
    const viewport = page.getViewport({ scale: 1 });
    const scale = targetWidth / viewport.width;
    const scaledViewport = page.getViewport({ scale });

    const canvas = document.createElement('canvas');
    canvas.width = scaledViewport.width;
    canvas.height = scaledViewport.height;
    const ctx = canvas.getContext('2d');

    await page.render({ canvasContext: ctx, viewport: scaledViewport }).promise;
    return canvas.toDataURL('image/jpeg', 0.85);
  } catch (err) {
    console.error('縮圖生成失敗:', err);
    return null;
  }
};

// 輔助函式：數字陣列轉為頁碼範圍字串 (如 [1, 2, 3, 5] -> "1-3, 5")
const numbersToRanges = (arr) => {
  if (!arr || arr.length === 0) return '';
  const sorted = [...new Set(arr)].sort((a, b) => a - b);
  const ranges = [];
  let start = sorted[0];
  let end = start;

  for (let i = 1; i < sorted.length; i++) {
    if (sorted[i] === end + 1) {
      end = sorted[i];
    } else {
      ranges.push(start === end ? `${start}` : `${start}-${end}`);
      start = sorted[i];
      end = start;
    }
  }
  ranges.push(start === end ? `${start}` : `${start}-${end}`);
  return ranges.join(', ');
};

// 輔助函式：範圍字串解析回數字集合 (如 "1-3, 5" -> [1, 2, 3, 5])
const rangesToNumbers = (str, maxPages) => {
  const pages = new Set();
  const parts = str.split(',').map(s => s.trim()).filter(Boolean);
  for (const part of parts) {
    if (part.includes('-')) {
      const [s, e] = part.split('-').map(Number);
      if (!isNaN(s) && !isNaN(e)) {
        const low = Math.max(1, Math.min(s, e));
        const high = Math.min(maxPages, Math.max(s, e));
        for (let i = low; i <= high; i++) pages.add(i);
      }
    } else {
      const n = Number(part);
      if (!isNaN(n) && n >= 1 && n <= maxPages) pages.add(n);
    }
  }
  return pages;
};

// 切換單頁勾選狀態
const togglePageSelection = (pageNum) => {
  if (selectedPages.value.has(pageNum)) {
    selectedPages.value.delete(pageNum);
  } else {
    selectedPages.value.add(pageNum);
  }
  splitParams.value.mode = 'ranges';
  splitParams.value.rangesStr = numbersToRanges(Array.from(selectedPages.value));
};

// 拆分快捷操作
const selectAllPages = () => {
  selectedPages.value = new Set(splitPages.value.map(p => p.pageNum));
  splitParams.value.rangesStr = numbersToRanges(Array.from(selectedPages.value));
};
const clearAllPages = () => {
  selectedPages.value.clear();
  splitParams.value.rangesStr = '';
};
const selectOddPages = () => {
  selectedPages.value = new Set(splitPages.value.filter(p => p.pageNum % 2 !== 0).map(p => p.pageNum));
  splitParams.value.rangesStr = numbersToRanges(Array.from(selectedPages.value));
};
const selectEvenPages = () => {
  selectedPages.value = new Set(splitPages.value.filter(p => p.pageNum % 2 === 0).map(p => p.pageNum));
  splitParams.value.rangesStr = numbersToRanges(Array.from(selectedPages.value));
};

// 當使用者手動在文字框輸入範圍時，雙向反選勾勾
const onRangesInput = () => {
  if (splitPages.value.length > 0) {
    selectedPages.value = rangesToNumbers(splitParams.value.rangesStr, splitPages.value.length);
  }
};

// ================= 檔案上傳與解析處理 =================
const appendFiles = async (fileList) => {
  for (let f of fileList) {
    const ext = f.name.split('.').pop().toLowerCase();
    const item = {
      id: Math.random().toString(36).substring(2, 9),
      name: f.name,
      size: f.size,
      ext: ext,
      rawFile: f,
      pages: null,
      thumbnail: null
    };

    // 若是圖片直接建立本地預覽
    if (f.type.startsWith('image/')) {
      item.thumbnail = URL.createObjectURL(f);
    }

    // 若是 PDF，利用 pdf.js 生成第 1 頁封面縮圖
    if (ext === 'pdf') {
      try {
        const arrayBuffer = await f.arrayBuffer();
        const pdfDoc = await pdfjsLib.getDocument({ data: arrayBuffer }).promise;
        item.pages = pdfDoc.numPages;
        item.thumbnail = await renderPageThumbnail(pdfDoc, 1, 160);

        // 如果當前是「拆分 PDF」，依序讀取所有頁面的縮圖
        if (currentToolId.value === 'split_pdf') {
          files.value = [item]; // 拆分一次處理單一檔案
          splitPages.value = [];
          selectedPages.value = new Set([1]); // 預設選取第 1 頁
          splitParams.value.rangesStr = '1';
          isRenderingPages.value = true;

          // 先建立佔位
          for (let i = 1; i <= pdfDoc.numPages; i++) {
            splitPages.value.push({ pageNum: i, thumbnail: null });
          }

          // 非同步循序生成各頁縮圖 (保持平滑不卡頓)
          (async () => {
            for (let i = 1; i <= pdfDoc.numPages; i++) {
              const thumb = await renderPageThumbnail(pdfDoc, i, 160);
              const target = splitPages.value.find(p => p.pageNum === i);
              if (target) target.thumbnail = thumb;
            }
            isRenderingPages.value = false;
          })();

          return;
        }
      } catch (err) {
        console.error('PDF 解析失敗:', err);
      }
    }

    files.value.push(item);
  }
};

const categories = [
  { id: 'all', name: '全部' },
  { id: 'workflow', name: '工作流程' },
  { id: 'organize', name: '整理 PDF' },
  { id: 'optimize', name: '優化 PDF' },
  { id: 'convert', name: 'PDF轉換' },
  { id: 'edit', name: '編輯PDF文檔' },
  { id: 'security', name: 'PDF 安全性' }
];

const makeIcon = (pathD, textBadge = null) => {
  return {
    render() {
      if (textBadge) {
        return h('span', { class: 'font-black text-base' }, textBadge);
      }
      return h('svg', { class: 'w-6 h-6 fill-current', viewBox: '0 0 24 24' }, [
        h('path', { d: pathD })
      ]);
    }
  };
};

const tools = [
  {
    id: 'merge_pdf',
    category: 'organize',
    title: '合併PDF',
    desc: '合併PDF文檔，並按照你的喜好排序，簡單又快速！',
    iconBg: 'bg-[#FF6B6B]',
    iconSvg: makeIcon('M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z'),
    enabled: true,
    accept: '.pdf',
    buttonText: '選擇多個 PDF 檔案',
    actionText: '合併 PDF →'
  },
  {
    id: 'split_pdf',
    category: 'organize',
    title: '拆分PDF',
    desc: '拆分出獨立頁面，或所有頁面，以便將其轉換為獨立的PDF文檔。',
    iconBg: 'bg-[#FECA57]',
    iconSvg: makeIcon('M9.64 7.64c.23-.5.36-1.05.36-1.64 0-2.21-1.79-4-4-4S2 3.79 2 6s1.79 4 4 4c.59 0 1.14-.13 1.64-.36L10 12l-2.36 2.36C7.14 14.13 6.59 14 6 14c-2.21 0-4 1.79-4 4s1.79 4 4 4 4-1.79 4-4c0-.59-.13-1.14-.36-1.64L12 14l7 7h3v-1L9.64 7.64zM6 8c-1.1 0-2-.9-2-2s.9-2 2-2 2 .9 2 2-.9 2-2 2zm0 12c-1.1 0-2-.9-2-2s.9-2 2-2 2 .9 2 2-.9 2-2 2zm6-7.5c-.28 0-.5-.22-.5-.5s.22-.5.5-.5.5.22.5.5-.22.5-.5.5zM19 3l-6 6 2 2 7-7V3h-3z'),
    enabled: true,
    accept: '.pdf',
    buttonText: '選擇 PDF 檔案',
    actionText: '拆分 PDF →'
  },
  {
    id: 'compress_pdf',
    category: 'optimize',
    title: '壓縮PDF',
    desc: '減小PDF文檔的尺寸，但同時保持最佳品質。',
    iconBg: 'bg-[#48DBFB]',
    iconSvg: makeIcon('M19 12h-2v3h-3v2h5v-5zM7 9h3V7H5v5h2V9zm14-6H3c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h18c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16.01H3V4.99h18v14.02z'),
    enabled: false
  },
  {
    id: 'pdf_to_word',
    category: 'convert',
    title: 'PDF 轉 Word',
    desc: '輕鬆地將PDF轉為可編輯的DOC和DOCX文檔。',
    iconBg: 'bg-[#1DD1A1]',
    iconSvg: makeIcon(null, 'W'),
    enabled: true,
    accept: '.pdf',
    buttonText: '選擇 PDF 檔案',
    actionText: '轉換為 Word →'
  },
  {
    id: 'pdf_to_ppt',
    category: 'convert',
    title: 'PDF 轉 PowerPoint',
    desc: '將你的PDF轉換為可編輯的PPT和PPTX幻燈片。',
    iconBg: 'bg-[#FF9F43]',
    iconSvg: makeIcon(null, 'P'),
    enabled: false
  },
  {
    id: 'pdf_to_excel',
    category: 'convert',
    title: 'PDF 轉 Excel',
    desc: '只需幾秒鐘，即可將數據直接從PDF文檔抽取至Excel中。',
    iconBg: 'bg-[#5F27CD]',
    iconSvg: makeIcon(null, 'X'),
    enabled: false
  },
  {
    id: 'word_to_pdf',
    category: 'convert',
    title: 'Word 轉 PDF',
    desc: '將DOC或DOCX轉換為PDF文檔，保持最佳品質。',
    iconBg: 'bg-[#54A0FF]',
    iconSvg: makeIcon(null, 'W'),
    enabled: true,
    accept: '.docx,.doc',
    buttonText: '選擇 Word 文件',
    actionText: '轉換為 PDF →'
  },
  {
    id: 'ppt_to_pdf',
    category: 'convert',
    title: 'PowerPoint 轉 PDF',
    desc: '將PPT轉換為PDF文檔，保持最佳品質。',
    iconBg: 'bg-[#FF9F43]',
    iconSvg: makeIcon(null, 'P'),
    enabled: false
  },
  {
    id: 'excel_to_pdf',
    category: 'convert',
    title: 'Excel 轉 PDF',
    desc: '將EXCEL表格轉換為PDF文檔，以方便瀏覽。',
    iconBg: 'bg-[#10AC84]',
    iconSvg: makeIcon(null, 'X'),
    enabled: false
  },
  {
    id: 'edit_pdf',
    category: 'edit',
    title: '編輯PDF文檔',
    desc: '給PDF文檔添加文本、圖片、形狀或者手寫註釋。',
    iconBg: 'bg-[#C8D6E5]',
    iconSvg: makeIcon('M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04c.39-.39.39-1.02 0-1.41l-2.34-2.34c-.39-.39-1.02-.39-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z'),
    enabled: false
  },
  {
    id: 'pdf_to_jpg',
    category: 'convert',
    title: 'PDF轉JPG',
    desc: '提取PDF文檔中的所有圖片，或將每一頁轉存為JPG。',
    iconBg: 'bg-[#FECA57]',
    iconSvg: makeIcon('M21 19V5c0-1.1-.9-2-2-2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2zM8.5 13.5l2.5 3.01L14.5 12l4.5 6H5l3.5-4.5z'),
    enabled: true,
    accept: '.pdf',
    buttonText: '選擇 PDF 檔案',
    actionText: '轉換為 JPG →'
  },
  {
    id: 'jpg_to_pdf',
    category: 'convert',
    title: 'JPG轉PDF',
    desc: '將你的圖片轉換為PDF文檔。可以調整方向和邊距。',
    iconBg: 'bg-[#FF6B6B]',
    iconSvg: makeIcon('M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z'),
    enabled: true,
    accept: '.jpg,.jpeg,.png',
    buttonText: '選擇多張圖片',
    actionText: '合併為 PDF →'
  }
];

const filteredTools = computed(() => {
  if (activeCategory.value === 'all') return tools;
  return tools.filter(t => t.category === activeCategory.value);
});

const activeToolMeta = computed(() => {
  return tools.find(t => t.id === currentToolId.value) || tools[0];
});

const totalBytes = computed(() => {
  return files.value.reduce((acc, f) => acc + f.size, 0);
});

const onCardClick = (tool) => {
  if (!tool.enabled) {
    alert(`「${tool.title}」功能預計於下個版本更新！\n目前核心支援：合併、拆分、PDF↔Word、PDF↔JPG。`);
    return;
  }
  selectTool(tool.id);
};

const selectTool = (toolId) => {
  currentToolId.value = toolId;
  files.value = [];
  splitPages.value = [];
  selectedPages.value.clear();
  currentStep.value = 'workspace';
};

const goToHome = () => {
  files.value = [];
  splitPages.value = [];
  selectedPages.value.clear();
  currentStep.value = 'hub';
};

const clearWorkspace = () => {
  files.value = [];
  splitPages.value = [];
  selectedPages.value.clear();
};

const triggerFileInput = () => fileInputRef.value.click();

const handleFileInput = (e) => {
  appendFiles(e.target.files);
  e.target.value = '';
};

const handleDrop = (e) => {
  isDragging.value = false;
  appendFiles(e.dataTransfer.files);
};

const removeFile = (index) => files.value.splice(index, 1);

const moveFile = (index, offset) => {
  const target = index + offset;
  if (target < 0 || target >= files.value.length) return;
  const temp = files.value[index];
  files.value[index] = files.value[target];
  files.value[target] = temp;
};

const formatSize = (b) => {
  if (b < 1048576) return (b / 1024).toFixed(1) + ' KB';
  return (b / 1048576).toFixed(1) + ' MB';
};

const executeTool = async () => {
  if (files.value.length === 0) return;

  if (currentToolId.value === 'split_pdf' && splitParams.value.mode === 'ranges' && !splitParams.value.rangesStr.trim()) {
    alert('請至少勾選一頁或輸入拆分範圍！');
    return;
  }

  isProcessing.value = true;
  progress.value = 25;
  progressText.value = '正在把饅頭放進蒸籠...';

  const formData = new FormData();
  files.value.forEach(item => {
    formData.append('files', item.rawFile);
  });
  formData.append('mode', currentToolId.value);

  if (currentToolId.value === 'split_pdf') {
    formData.append('split_mode', splitParams.value.mode);
    formData.append('ranges_str', splitParams.value.rangesStr);
    formData.append('chunk_size', splitParams.value.chunkSize);
  }

  try {
    progress.value = 65;
    progressText.value = '正在努力加熱中... ♨️';

    const res = await fetch('/api/convert', { method: 'POST', body: formData });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || '轉檔失敗');
    }

    const data = await res.json();
    progress.value = 100;
    downloadUrl.value = data.download_url;
    downloadFilename.value = data.filename;
    currentStep.value = 'success';
  } catch (err) {
    alert(`執行失敗: ${err.message}`);
  } finally {
    isProcessing.value = false;
  }
};
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@700;800;900&family=Noto+Sans+TC:wght@500;700;900&display=swap');

.font-cartoon {
  font-family: 'Nunito', 'Noto Sans TC', sans-serif;
}

html, body {
  margin: 0;
  padding: 0;
  min-height: 100%;
}

.bg-dots {
  background-image: radial-gradient(#E5D9B6 2px, transparent 2px);
  background-size: 30px 30px;
  background-color: #FFF9E6;
}

.cartoon-btn {
  transition: all 0.15s cubic-bezier(0.34, 1.56, 0.64, 1);
}
.cartoon-btn:hover {
  transform: translate(-2px, -2px);
  box-shadow: 6px 6px 0px #2C3E50 !important;
}
.cartoon-btn:active {
  transform: translate(4px, 4px);
  box-shadow: 1px 1px 0px #2C3E50 !important;
}

.cartoon-card {
  transition: all 0.2s cubic-bezier(0.34, 1.56, 0.64, 1);
}
.cartoon-card:hover {
  transform: translateY(-6px) rotate(1deg);
  box-shadow: 8px 10px 0px #2C3E50 !important;
}
.cartoon-card:active {
  transform: translateY(2px);
  box-shadow: 2px 2px 0px #2C3E50 !important;
}
</style>