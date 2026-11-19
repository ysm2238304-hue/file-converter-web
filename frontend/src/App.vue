<template>
  <div class="min-h-screen w-full bg-[#FFF9E6] bg-dots text-[#2C3E50] font-cartoon antialiased flex flex-col relative selection:bg-[#FF6B6B] selection:text-white">
    
    <!-- ================= 全域卡通 Toast 通知條 ================= -->
    <Transition name="toast">
      <div 
        v-if="toast.show"
        :class="[
          'fixed top-24 right-4 sm:right-8 z-[60] max-w-sm px-4 py-3 rounded-2xl border-[3px] border-[#2C3E50] shadow-[4px_4px_0px_#2C3E50] flex items-center gap-3 font-black text-sm',
          toast.type === 'error' ? 'bg-[#FFE5E5] text-[#C0392B]' : 'bg-[#E6FFF5] text-[#0F766E]'
        ]"
      >
        <span class="text-lg shrink-0">{{ toast.type === 'error' ? '⚠️' : '✅' }}</span>
        <span class="flex-1 leading-snug">{{ toast.message }}</span>
        <button @click="toast.show = false" class="text-xs opacity-60 hover:opacity-100 cursor-pointer">✕</button>
      </div>
    </Transition>

    <!-- ================= 1. 卡通風格頂部導航列 ================= -->
    <header class="bg-white/95 backdrop-blur-sm border-b-[3px] border-[#2C3E50] sticky top-0 z-50">
      <div class="max-w-[1440px] mx-auto px-4 sm:px-8 h-18 sm:h-20 flex items-center justify-between gap-4">
        
        <div class="flex items-center space-x-6 lg:space-x-8">
          <div @click="goToHome" class="flex items-center space-x-2.5 cursor-pointer select-none group">
            <span class="bg-[#FF6B6B] text-white px-3 py-1 rounded-xl border-[3px] border-[#2C3E50] shadow-[3px_3px_0px_#2C3E50] -rotate-3 text-lg sm:text-xl font-black group-hover:rotate-0 transition-transform">
              PDF
            </span>
            <span class="text-xl sm:text-2xl font-black tracking-tight text-[#2C3E50]">黑糖饅頭 🥟</span>
          </div>

          <nav class="hidden md:flex items-center space-x-2 text-sm font-black text-[#2C3E50]">
            <button 
              v-for="navId in ['merge_pdf', 'organize_pdf', 'compress_pdf', 'heic_to_jpg']" 
              :key="navId"
              @click="selectTool(navId)"
              :class="[
                'px-3 py-1.5 rounded-xl transition-colors cursor-pointer',
                currentStep === 'workspace' && currentToolId === navId 
                  ? 'bg-[#FFF3CD] text-[#FF6B6B] border-[2px] border-[#2C3E50]' 
                  : 'hover:bg-[#FFF9E6] hover:text-[#FF6B6B]'
              ]"
            >
              {{ getToolTitle(navId) }}
            </button>
            <button @click="goToHome" class="px-3 py-1.5 rounded-xl hover:bg-[#FFF9E6] hover:text-[#FF6B6B] transition-colors cursor-pointer">
              所有工具 ▾
            </button>
          </nav>
        </div>

        <div class="flex items-center gap-3">
          <button 
            @click="openFeedbackModal" 
            class="cartoon-btn px-4 py-2 sm:px-5 sm:py-2.5 rounded-xl bg-[#FECA57] border-[3px] border-[#2C3E50] shadow-[3px_3px_0px_#2C3E50] text-[#2C3E50] text-xs sm:text-sm font-black flex items-center gap-1.5 cursor-pointer"
          >
            <span>💬</span>
            <span>問題回報</span>
          </button>
        </div>
      </div>
    </header>

    <!-- ================= 2. 主內容區域 ================= -->
    <main class="flex-1 flex flex-col relative w-full">

      <!-- ================= 視圖 1：首頁工具大廳 ================= -->
      <section v-if="currentStep === 'hub'" class="max-w-6xl mx-auto px-4 sm:px-8 py-8 sm:py-10 w-full space-y-8 relative z-10">
        
        <div class="text-center space-y-3 max-w-3xl mx-auto pt-2">
          <h1 class="text-3xl sm:text-5xl font-black text-[#2C3E50] tracking-tight leading-tight">
            <span class="relative inline-block">
              <span class="relative z-10 px-2">黑糖饅頭很好吃</span>
              <span class="absolute bottom-1.5 left-0 w-full h-3.5 sm:h-5 bg-[#FECA57] -rotate-1 rounded-lg border-[2px] border-[#2C3E50] -z-0"></span>
            </span>
            🥟
          </h1>
          <p class="text-sm sm:text-base font-bold text-gray-500 max-w-xl mx-auto">
            完全免費、免註冊！整理旋轉、極限壓縮、HEIC 轉檔、加密解鎖一站搞定 ✨
          </p>
        </div>

        <!-- 分類切換膠囊列 -->
        <div class="flex items-center justify-center flex-wrap gap-2.5">
          <button 
            v-for="cat in categories" 
            :key="cat.id"
            @click="activeCategory = cat.id"
            :class="[
              'px-4 py-1.5 rounded-full text-sm font-black border-[3px] transition-all duration-150 cursor-pointer',
              activeCategory === cat.id 
                ? 'bg-[#FF6B6B] text-white border-[#2C3E50] shadow-[3px_3px_0px_#2C3E50] -translate-y-0.5' 
                : 'bg-white text-[#2C3E50] border-[#2C3E50] shadow-[2px_2px_0px_#2C3E50] hover:-translate-y-0.5'
            ]"
          >
            {{ cat.name }}
            <span class="ml-1 text-[11px] opacity-80">({{ getCategoryCount(cat.id) }})</span>
          </button>
        </div>

        <!-- 卡通卡片網格 -->
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5 pt-2">
          <div 
            v-for="tool in filteredTools" 
            :key="tool.id"
            @click="selectTool(tool.id)"
            class="group bg-white rounded-3xl border-[3px] border-[#2C3E50] p-5 flex flex-col justify-between gap-4 transition-all duration-200 select-none cartoon-card shadow-[5px_5px_0px_#2C3E50] cursor-pointer hover:bg-[#FFFDF5]"
          >
            <div class="flex items-start gap-4">
              <div :class="['w-12 h-12 shrink-0 rounded-2xl flex items-center justify-center text-white border-[3px] border-[#2C3E50] shadow-[2px_2px_0px_#2C3E50] transition-transform group-hover:scale-105', tool.iconBg]">
                <component :is="tool.iconSvg" />
              </div>

              <div class="space-y-1 flex-1 min-w-0">
                <div class="flex items-center justify-between gap-2">
                  <h3 class="text-lg font-black text-[#2C3E50] leading-snug truncate">
                    {{ tool.title }}
                  </h3>
                  <span class="text-xs font-black text-gray-300 group-hover:text-[#FF6B6B] transition-colors">→</span>
                </div>
                <p class="text-xs font-bold text-gray-500 leading-relaxed line-clamp-2">
                  {{ tool.desc }}
                </p>
              </div>
            </div>

            <div class="flex items-center justify-between pt-3 border-t-[2px] border-dashed border-slate-200">
              <div class="flex flex-wrap gap-1.5">
                <span 
                  v-for="badge in tool.badges" 
                  :key="badge"
                  class="px-2 py-0.5 text-[10px] font-black bg-[#F0F4F8] text-[#2C3E50] border-[1.5px] border-[#2C3E50] rounded-md"
                >
                  {{ badge }}
                </span>
              </div>
              <span class="text-[11px] font-black text-[#FF6B6B] opacity-0 group-hover:opacity-100 transition-opacity">
                立即使用
              </span>
            </div>
          </div>
        </div>
      </section>

      <!-- ================= 視圖 2：獨立工具工作台 (Workspace) ================= -->
      <section v-else-if="currentStep === 'workspace'" class="flex-1 flex flex-col relative z-10">
        
        <input 
          type="file" 
          ref="fileInputRef" 
          multiple 
          class="hidden" 
          :accept="activeToolMeta.accept"
          @change="handleFileInput" 
        />

        <!-- 頂部工具切換列 -->
        <div class="bg-white border-b-[3px] border-[#2C3E50] py-3 px-4 sm:px-6 shadow-xs">
          <div class="max-w-[1440px] mx-auto flex flex-wrap items-center justify-between gap-3">
            <div class="flex items-center gap-3">
              <button @click="goToHome" class="text-xs sm:text-sm font-black text-[#2C3E50] hover:text-[#FF6B6B] flex items-center gap-1 bg-[#F0F4F8] px-3 py-1.5 rounded-xl border-[2px] border-[#2C3E50] shadow-[2px_2px_0px_#2C3E50] cartoon-btn cursor-pointer">
                <span>← 大廳</span>
              </button>
              <div class="flex items-center gap-2">
                <span :class="['w-8 h-8 rounded-xl flex items-center justify-center text-white border-[2px] border-[#2C3E50]', activeToolMeta.iconBg]">
                  <component :is="activeToolMeta.iconSvg" />
                </span>
                <span class="text-base sm:text-lg font-black text-[#2C3E50]">{{ activeToolMeta.title }}</span>
              </div>
            </div>

            <div class="flex items-center gap-1.5 overflow-x-auto max-w-full py-1">
              <button
                v-for="t in tools"
                :key="t.id"
                @click="selectTool(t.id)"
                :class="[
                  'px-2.5 py-1 rounded-lg text-xs font-black whitespace-nowrap border-[2px] transition-all cursor-pointer',
                  currentToolId === t.id
                    ? 'bg-[#FECA57] text-[#2C3E50] border-[#2C3E50] shadow-[2px_2px_0px_#2C3E50]'
                    : 'bg-[#F8FAFC] text-gray-500 border-transparent hover:border-[#2C3E50] hover:text-[#2C3E50]'
                ]"
              >
                {{ t.title }}
              </button>
            </div>

            <button v-if="files.length > 0" @click="clearWorkspace" class="text-xs font-black text-slate-400 hover:text-[#FF6B6B] cursor-pointer">
              清空檔案
            </button>
          </div>
        </div>

        <!-- 尚未選擇檔案：上傳區 -->
        <div v-if="files.length === 0" class="flex-1 flex items-center justify-center p-6 min-h-[60vh]">
          <div 
            @dragover.prevent="isDragging = true"
            @dragleave.prevent="isDragging = false"
            @drop.prevent="handleDrop"
            :class="[
              'max-w-2xl w-full p-10 sm:p-12 text-center rounded-[2rem] border-[4px] border-dashed transition-all duration-200 flex flex-col items-center justify-center space-y-6 bg-white',
              isDragging ? 'border-[#FF6B6B] bg-[#FFF0F0] scale-[1.02] shadow-[8px_8px_0px_#FF6B6B]' : 'border-[#2C3E50] shadow-[8px_8px_0px_#2C3E50]'
            ]"
          >
            <div class="w-20 h-20 rounded-3xl bg-[#FFF9E6] border-[3px] border-[#2C3E50] shadow-[4px_4px_0px_#2C3E50] flex items-center justify-center text-5xl">
              📂
            </div>
            
            <div class="space-y-2">
              <h2 class="text-2xl sm:text-3xl font-black text-[#2C3E50]">{{ activeToolMeta.title }}</h2>
              <p class="text-sm font-bold text-gray-500 max-w-md mx-auto">{{ activeToolMeta.desc }}</p>
              <div class="flex items-center justify-center flex-wrap gap-1.5 pt-1">
                <span 
                  v-for="badge in activeToolMeta.badges" 
                  :key="badge"
                  class="px-2.5 py-0.5 text-xs font-black bg-[#F0F4F8] text-[#2C3E50] border-[2px] border-[#2C3E50] rounded-lg"
                >
                  支援 {{ badge }}
                </span>
                <span v-if="isImageBatchTool" class="px-2.5 py-0.5 text-xs font-black text-[#FF6B6B] bg-[#FFF0F0] border-[2px] border-[#FF6B6B] rounded-lg">
                  上限 {{ MAX_IMAGE_COUNT }} 張 / 50 MB
                </span>
              </div>
            </div>

            <button 
              @click="triggerFileInput"
              class="cartoon-btn px-10 py-4 rounded-2xl bg-[#48DBFB] text-[#2C3E50] border-[3px] border-[#2C3E50] shadow-[5px_5px_0px_#2C3E50] font-black text-lg transition-all cursor-pointer"
            >
              {{ activeToolMeta.buttonText }}
            </button>

            <p class="text-xs font-bold text-gray-400">或直接把檔案拖放到這裡 ✨</p>
          </div>
        </div>

        <!-- 已選擇檔案區塊 -->
        <div v-else class="flex-1 max-w-[1440px] w-full mx-auto p-4 sm:p-8 grid grid-cols-1 lg:grid-cols-4 gap-6 lg:gap-8 items-start">
          
          <!-- ================= 左側區域 ================= -->
          <div class="lg:col-span-3 space-y-5">
            
            <!-- 情況 A：拆分 PDF 模式（全部頁面縮圖矩陣） -->
            <div v-if="currentToolId === 'split_pdf'" class="space-y-4">
              <div class="flex flex-wrap items-center justify-between gap-3 bg-white p-4 rounded-2xl border-[3px] border-[#2C3E50] shadow-[4px_4px_0px_#2C3E50]">
                <div class="flex items-center gap-2">
                  <span class="text-sm font-black text-[#2C3E50]">
                    📄 {{ files[0]?.name }} (共 {{ splitPages.length }} 頁)
                  </span>
                  <span v-if="isRenderingPages" class="text-xs font-bold text-[#FF6B6B] animate-pulse">
                    縮圖生成中... ⏳
                  </span>
                </div>

                <div class="flex flex-wrap items-center gap-2">
                  <button @click="selectAllPages" class="px-2.5 py-1 text-xs font-black bg-[#F0F4F8] hover:bg-[#FECA57] border-[2px] border-[#2C3E50] rounded-lg shadow-[1px_1px_0px_#2C3E50] transition-colors cursor-pointer">全選</button>
                  <button @click="clearAllPages" class="px-2.5 py-1 text-xs font-black bg-[#F0F4F8] hover:bg-[#FF6B6B] hover:text-white border-[2px] border-[#2C3E50] rounded-lg shadow-[1px_1px_0px_#2C3E50] transition-colors cursor-pointer">清空</button>
                  <button @click="selectOddPages" class="px-2.5 py-1 text-xs font-black bg-[#F0F4F8] hover:bg-[#FECA57] border-[2px] border-[#2C3E50] rounded-lg shadow-[1px_1px_0px_#2C3E50] transition-colors cursor-pointer">奇數頁</button>
                  <button @click="selectEvenPages" class="px-2.5 py-1 text-xs font-black bg-[#F0F4F8] hover:bg-[#FECA57] border-[2px] border-[#2C3E50] rounded-lg shadow-[1px_1px_0px_#2C3E50] transition-colors cursor-pointer">偶數頁</button>
                  <button @click="triggerFileInput" class="text-xs font-black text-[#FF6B6B] bg-[#FFF0F0] px-3 py-1 rounded-lg border-[2px] border-[#FF6B6B] cursor-pointer">更換檔案</button>
                </div>
              </div>

              <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 xl:grid-cols-5 gap-4">
                <div 
                  v-for="page in splitPages" 
                  :key="page.pageNum"
                  @click="togglePageSelection(page.pageNum)"
                  :class="[
                    'group bg-white rounded-2xl border-[3px] p-2 relative flex flex-col justify-between aspect-[3/4] cursor-pointer transition-all duration-150 select-none',
                    selectedPages.has(page.pageNum) 
                      ? 'border-[#FF6B6B] bg-[#FFF8F8] shadow-[5px_5px_0px_#FF6B6B] -translate-y-1' 
                      : 'border-[#2C3E50] shadow-[3px_3px_0px_#2C3E50] opacity-85 hover:opacity-100 hover:shadow-[5px_5px_0px_#2C3E50]'
                  ]"
                >
                  <div class="absolute top-2.5 left-2.5 w-7 h-7 rounded-full bg-[#FECA57] border-[2px] border-[#2C3E50] text-[#2C3E50] text-xs font-black flex items-center justify-center shadow-[1px_1px_0px_#2C3E50] z-10">
                    {{ page.pageNum }}
                  </div>

                  <div 
                    v-if="selectedPages.has(page.pageNum)"
                    class="absolute top-2.5 right-2.5 w-7 h-7 rounded-full bg-[#1DD1A1] border-[2px] border-[#2C3E50] text-white text-xs font-black flex items-center justify-center shadow-[1px_1px_0px_#2C3E50] z-10"
                  >
                    ✓
                  </div>

                  <div class="flex-1 flex items-center justify-center overflow-hidden rounded-xl border-[2px] border-slate-200 bg-[#F9FAFB] my-1 p-1">
                    <img 
                      v-if="page.thumbnail" 
                      :src="page.thumbnail" 
                      class="max-w-full max-h-full object-contain pointer-events-none" 
                    />
                    <div v-else class="text-xs font-bold text-gray-300 flex flex-col items-center gap-1">
                      <span class="animate-spin text-lg">⏳</span>
                      <span>加載中</span>
                    </div>
                  </div>

                  <div class="text-center text-[11px] font-black" :class="selectedPages.has(page.pageNum) ? 'text-[#FF6B6B]' : 'text-gray-400'">
                    {{ selectedPages.has(page.pageNum) ? '已選取' : '點擊加入' }}
                  </div>
                </div>
              </div>
            </div>

            <!-- 情況 B：PDF 旋轉與刪頁整理模式 -->
            <div v-else-if="currentToolId === 'organize_pdf'" class="space-y-4">
              <div class="flex flex-wrap items-center justify-between gap-3 bg-white p-4 rounded-2xl border-[3px] border-[#2C3E50] shadow-[4px_4px_0px_#2C3E50]">
                <div class="flex items-center gap-2">
                  <span class="text-sm font-black text-[#2C3E50]">
                    📄 {{ files[0]?.name }} (保留 {{ organizePages.length }} / {{ files[0]?.pages || organizePages.length }} 頁)
                  </span>
                  <span v-if="isRenderingPages" class="text-xs font-bold text-[#FF6B6B] animate-pulse">
                    縮圖生成中... ⏳
                  </span>
                </div>

                <div class="flex flex-wrap items-center gap-2">
                  <button @click="rotateAllOrganizePages(90)" class="px-2.5 py-1 text-xs font-black bg-[#F0F4F8] hover:bg-[#FECA57] border-[2px] border-[#2C3E50] rounded-lg shadow-[1px_1px_0px_#2C3E50] cursor-pointer">全部右轉 90°</button>
                  <button @click="resetOrganizePages" class="px-2.5 py-1 text-xs font-black bg-[#F0F4F8] hover:bg-[#48DBFB] border-[2px] border-[#2C3E50] rounded-lg shadow-[1px_1px_0px_#2C3E50] cursor-pointer">全部重置</button>
                  <button @click="triggerFileInput" class="text-xs font-black text-[#FF6B6B] bg-[#FFF0F0] px-3 py-1 rounded-lg border-[2px] border-[#FF6B6B] cursor-pointer">更換檔案</button>
                </div>
              </div>

              <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 xl:grid-cols-5 gap-4">
                <div 
                  v-for="(page, idx) in organizePages" 
                  :key="page.uid"
                  class="bg-white rounded-2xl border-[3px] border-[#2C3E50] shadow-[4px_4px_0px_#2C3E50] p-2.5 relative flex flex-col justify-between aspect-[3/4]"
                >
                  <div class="absolute top-2.5 left-2.5 px-2 h-6 rounded-full bg-[#FECA57] border-[2px] border-[#2C3E50] text-[#2C3E50] text-[11px] font-black flex items-center justify-center shadow-[1px_1px_0px_#2C3E50] z-10">
                    #{{ idx + 1 }} <span class="opacity-60 ml-1">(原P{{ page.pageNum }})</span>
                  </div>

                  <button 
                    @click="removeOrganizePage(idx)"
                    title="刪除此頁"
                    class="absolute top-2.5 right-2.5 w-6 h-6 rounded-full bg-white border-[2px] border-[#2C3E50] text-[#2C3E50] hover:bg-[#FF6B6B] hover:text-white flex items-center justify-center text-[11px] font-black shadow-[1px_1px_0px_#2C3E50] z-10 cursor-pointer"
                  >
                    ✕
                  </button>

                  <div class="flex-1 flex items-center justify-center overflow-hidden rounded-xl border-[2px] border-slate-200 bg-[#F9FAFB] my-1 p-2">
                    <img 
                      v-if="page.thumbnail" 
                      :src="page.thumbnail" 
                      :style="{ transform: `rotate(${page.rotate}deg)` }"
                      class="max-w-full max-h-full object-contain transition-transform duration-200 pointer-events-none" 
                    />
                    <div v-else class="text-xs font-bold text-gray-300 flex flex-col items-center gap-1">
                      <span class="animate-spin text-lg">⏳</span>
                      <span>加載中</span>
                    </div>
                  </div>

                  <div class="flex items-center justify-between pt-1.5 border-t-[2px] border-slate-100 text-xs font-black">
                    <button :disabled="idx === 0" @click="moveOrganizePage(idx, -1)" class="px-1.5 py-0.5 hover:text-[#FF6B6B] disabled:opacity-20 cursor-pointer">◀</button>
                    <div class="flex items-center gap-1">
                      <button @click="rotateOrganizePage(idx, -90)" title="左轉 90°" class="px-1.5 py-0.5 bg-[#F0F4F8] hover:bg-[#FECA57] rounded border border-[#2C3E50] cursor-pointer">↺</button>
                      <button @click="rotateOrganizePage(idx, 90)" title="右轉 90°" class="px-1.5 py-0.5 bg-[#F0F4F8] hover:bg-[#FECA57] rounded border border-[#2C3E50] cursor-pointer">↻</button>
                    </div>
                    <button :disabled="idx === organizePages.length - 1" @click="moveOrganizePage(idx, 1)" class="px-1.5 py-0.5 hover:text-[#FF6B6B] disabled:opacity-20 cursor-pointer">▶</button>
                  </div>
                </div>
              </div>
            </div>

            <!-- 情況 C：其他功能（支援拖曳排序的檔案卡片網格） -->
            <div v-else class="space-y-4">
              <div class="flex flex-wrap items-center justify-between gap-2 bg-white p-4 rounded-2xl border-[3px] border-[#2C3E50] shadow-[4px_4px_0px_#2C3E50]">
                <div class="flex items-center gap-2">
                  <span class="text-sm font-black text-[#2C3E50]">
                    已選取 {{ files.length }} 個檔案
                  </span>
                  <span v-if="files.length > 1" class="text-xs font-bold text-gray-400 hidden sm:inline">
                    · 可直接拖曳卡片調換順序
                  </span>
                </div>
                <button @click="triggerFileInput" class="text-sm font-black text-[#FF6B6B] bg-[#FFF0F0] hover:bg-[#FFE0E0] px-3.5 py-1.5 rounded-xl border-[2px] border-[#FF6B6B] cursor-pointer transition-colors">
                  ➕ 新增檔案
                </button>
              </div>

              <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-5">
                <div 
                  v-for="(item, index) in files" 
                  :key="item.id"
                  draggable="true"
                  @dragstart="onDragStart(index)"
                  @dragover.prevent="dragOverIndex = index"
                  @dragleave="dragOverIndex = null"
                  @drop.prevent="onDropReorder(index)"
                  :class="[
                    'group bg-white rounded-2xl border-[3px] p-3 relative flex flex-col justify-between aspect-[3/4] transition-all cursor-grab active:cursor-grabbing',
                    dragOverIndex === index 
                      ? 'border-[#48DBFB] scale-[1.03] shadow-[6px_6px_0px_#48DBFB]' 
                      : 'border-[#2C3E50] shadow-[4px_4px_0px_#2C3E50] hover:-translate-y-1'
                  ]"
                >
                  <div class="absolute top-3 left-3 w-7 h-7 rounded-full bg-[#FECA57] border-[2px] border-[#2C3E50] text-[#2C3E50] text-xs font-black flex items-center justify-center shadow-[1px_1px_0px_#2C3E50] z-10">
                    {{ index + 1 }}
                  </div>

                  <button 
                    @click="removeFile(index)"
                    class="absolute top-3 right-3 w-7 h-7 rounded-full bg-white border-[2px] border-[#2C3E50] text-[#2C3E50] hover:bg-[#FF6B6B] hover:text-white flex items-center justify-center text-xs transition-colors shadow-[1px_1px_0px_#2C3E50] z-10 cursor-pointer"
                  >
                    ✕
                  </button>

                  <div class="flex-1 flex flex-col items-center justify-center pt-2 overflow-hidden">
                    <div class="w-20 h-28 bg-[#F0F4F8] border-[2px] border-[#2C3E50] rounded-xl flex items-center justify-center shadow-[2px_2px_0px_#2C3E50] overflow-hidden p-1">
                      <img 
                        v-if="item.thumbnail" 
                        :src="item.thumbnail" 
                        class="max-w-full max-h-full object-contain rounded pointer-events-none" 
                      />
                      <span v-else class="text-xs font-black uppercase tracking-wider text-[#FF6B6B] bg-white px-2 py-1 rounded-md border border-[#2C3E50]">
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

                  <div class="flex items-center justify-center space-x-3 pt-2 border-t-[2px] border-slate-100 mt-2">
                    <button :disabled="index === 0" @click="moveFile(index, -1)" class="p-1 text-sm text-[#2C3E50] hover:text-[#FF6B6B] disabled:opacity-20 font-black cursor-pointer">◀</button>
                    <span class="text-[10px] text-slate-400 font-black tracking-widest">拖曳排序</span>
                    <button :disabled="index === files.length - 1" @click="moveFile(index, 1)" class="p-1 text-sm text-[#2C3E50] hover:text-[#FF6B6B] disabled:opacity-20 font-black cursor-pointer">▶</button>
                  </div>
                </div>
              </div>
            </div>

          </div>

          <!-- ================= 右側控制面板 ================= -->
          <div class="lg:col-span-1 bg-white p-6 rounded-[2rem] border-[3px] border-[#2C3E50] shadow-[6px_6px_0px_#2C3E50] space-y-5 sticky top-24">
            <div class="space-y-1">
              <h3 class="text-xl font-black text-[#2C3E50]">{{ activeToolMeta.title }}</h3>
              <p class="text-xs font-bold text-gray-400">配置你的專屬饅頭配方 ⚙️</p>
            </div>

            <!-- 1. 拆分 PDF 設定選項 -->
            <div v-if="currentToolId === 'split_pdf'" class="space-y-4 pt-4 border-t-[2px] border-slate-100">
              <label class="text-xs font-black text-[#2C3E50] block">分割模式</label>
              <div class="grid grid-cols-2 gap-2">
                <button
                  type="button"
                  @click="splitParams.mode = 'ranges'"
                  :class="[
                    'py-2 px-2 rounded-xl text-xs font-black border-[2px] border-[#2C3E50] cursor-pointer transition-all',
                    splitParams.mode === 'ranges' ? 'bg-[#FECA57] shadow-[2px_2px_0px_#2C3E50]' : 'bg-[#F0F4F8] text-gray-500'
                  ]"
                >
                  自選頁面
                </button>
                <button
                  type="button"
                  @click="splitParams.mode = 'all_single'"
                  :class="[
                    'py-2 px-2 rounded-xl text-xs font-black border-[2px] border-[#2C3E50] cursor-pointer transition-all',
                    splitParams.mode === 'all_single' ? 'bg-[#FECA57] shadow-[2px_2px_0px_#2C3E50]' : 'bg-[#F0F4F8] text-gray-500'
                  ]"
                >
                  全部拆單頁
                </button>
              </div>
              
              <div v-if="splitParams.mode === 'ranges'" class="space-y-1.5">
                <input 
                  v-model="splitParams.rangesStr" 
                  @input="onRangesInput"
                  type="text" 
                  placeholder="例如: 1-3, 5, 8-10" 
                  class="w-full px-3.5 py-2 text-sm font-bold bg-[#F0F4F8] border-[2px] border-[#2C3E50] rounded-xl focus:outline-none focus:ring-2 focus:ring-[#FF6B6B]" 
                />
                <p class="text-[11px] font-bold text-[#10AC84]">
                  即將抽出 {{ selectedPages.size }} 頁合併輸出
                </p>
              </div>
              <p v-else class="text-[11px] font-bold text-[#10AC84]">
                即將把 {{ splitPages.length }} 頁拆為獨立 PDF 並打包 ZIP
              </p>
            </div>

            <!-- 2. PDF 旋轉與刪頁整理摘要 -->
            <div v-else-if="currentToolId === 'organize_pdf'" class="space-y-3 pt-4 border-t-[2px] border-slate-100 text-xs font-bold text-gray-600">
              <div class="flex justify-between">
                <span>預計輸出頁數</span>
                <span class="font-black text-[#2C3E50]">{{ organizePages.length }} 頁</span>
              </div>
              <div class="flex justify-between">
                <span>已旋轉頁面</span>
                <span class="font-black text-[#FF6B6B]">{{ organizePages.filter(p => p.rotate % 360 !== 0).length }} 頁</span>
              </div>
              <p class="text-[11px] text-gray-400 leading-relaxed">
                點左側縮圖下方的 ↺ / ↻ 可旋轉，◀ / ▶ 調整頁序，右上角 ✕ 刪除不要的頁面。
              </p>
            </div>

            <!-- 3. PDF 加密 / 解鎖設定選項 -->
            <div v-else-if="currentToolId === 'security_pdf'" class="space-y-4 pt-4 border-t-[2px] border-slate-100">
              <div class="space-y-1.5">
                <label class="text-xs font-black text-[#2C3E50] block">處理模式</label>
                <div class="grid grid-cols-2 gap-2">
                  <button
                    type="button"
                    @click="securityParams.action = 'encrypt'"
                    :class="[
                      'py-2 rounded-xl text-xs font-black border-[2px] border-[#2C3E50] cursor-pointer transition-all',
                      securityParams.action === 'encrypt' ? 'bg-[#5F27CD] text-white shadow-[2px_2px_0px_#2C3E50]' : 'bg-[#F0F4F8] text-gray-500'
                    ]"
                  >
                    🔒 設定密碼
                  </button>
                  <button
                    type="button"
                    @click="securityParams.action = 'unlock'"
                    :class="[
                      'py-2 rounded-xl text-xs font-black border-[2px] border-[#2C3E50] cursor-pointer transition-all',
                      securityParams.action === 'unlock' ? 'bg-[#1DD1A1] text-white shadow-[2px_2px_0px_#2C3E50]' : 'bg-[#F0F4F8] text-gray-500'
                    ]"
                  >
                    🔓 解除密碼
                  </button>
                </div>
              </div>

              <div class="space-y-1.5">
                <label class="text-xs font-black text-[#2C3E50] block">
                  {{ securityParams.action === 'encrypt' ? '設定開啟密碼 (AES-256)' : '輸入原本的 PDF 密碼' }}
                </label>
                <div class="relative">
                  <input 
                    v-model="securityParams.password"
                    :type="securityParams.showPassword ? 'text' : 'password'"
                    placeholder="請輸入密碼..."
                    class="w-full pl-3.5 pr-10 py-2 text-sm font-bold bg-[#F0F4F8] border-[2px] border-[#2C3E50] rounded-xl focus:outline-none focus:ring-2 focus:ring-[#5F27CD]"
                  />
                  <button
                    type="button"
                    @click="securityParams.showPassword = !securityParams.showPassword"
                    class="absolute right-2.5 top-1/2 -translate-y-1/2 text-xs font-black text-gray-500 hover:text-[#2C3E50] cursor-pointer"
                  >
                    {{ securityParams.showPassword ? '隱藏' : '顯示' }}
                  </button>
                </div>
              </div>
            </div>

            <!-- 4. 照片排版成 A4 PDF 設定選項 -->
            <div v-else-if="currentToolId === 'images_to_a4_pdf'" class="space-y-4 pt-4 border-t-[2px] border-slate-100">
              <div class="space-y-1.5">
                <label class="text-xs font-black text-[#2C3E50] block">每頁照片張數</label>
                <div class="grid grid-cols-3 gap-2">
                  <button
                    v-for="opt in [{ id: '1_up', label: '1張/頁' }, { id: '2_up', label: '2張/頁' }, { id: '4_up', label: '4張/頁' }]"
                    :key="opt.id"
                    type="button"
                    @click="a4Params.layout = opt.id"
                    :class="[
                      'py-2 rounded-xl text-xs font-black border-[2px] border-[#2C3E50] cursor-pointer transition-all',
                      a4Params.layout === opt.id ? 'bg-[#FECA57] shadow-[2px_2px_0px_#2C3E50]' : 'bg-[#F0F4F8] text-gray-500'
                    ]"
                  >
                    {{ opt.label }}
                  </button>
                </div>
              </div>

              <div class="space-y-1.5">
                <label class="text-xs font-black text-[#2C3E50] block">A4 紙張方向</label>
                <div class="grid grid-cols-2 gap-2">
                  <button
                    type="button"
                    @click="a4Params.orientation = 'portrait'"
                    :class="[
                      'py-2 rounded-xl text-xs font-black border-[2px] border-[#2C3E50] cursor-pointer transition-all',
                      a4Params.orientation === 'portrait' ? 'bg-[#48DBFB] shadow-[2px_2px_0px_#2C3E50]' : 'bg-[#F0F4F8] text-gray-500'
                    ]"
                  >
                    直式 A4
                  </button>
                  <button
                    type="button"
                    @click="a4Params.orientation = 'landscape'"
                    :class="[
                      'py-2 rounded-xl text-xs font-black border-[2px] border-[#2C3E50] cursor-pointer transition-all',
                      a4Params.orientation === 'landscape' ? 'bg-[#48DBFB] shadow-[2px_2px_0px_#2C3E50]' : 'bg-[#F0F4F8] text-gray-500'
                    ]"
                  >
                    橫式 A4
                  </button>
                </div>
              </div>
              <p class="text-[11px] font-bold text-gray-400">支援拖曳左側卡片調整照片先後順序，含 HEIC 自動轉正 ✨</p>
            </div>

            <!-- 5. PDF 極限壓縮設定選項 -->
            <div v-else-if="currentToolId === 'compress_pdf'" class="space-y-4 pt-4 border-t-[2px] border-slate-100">
              <div class="space-y-1.5">
                <label class="text-xs font-black text-[#2C3E50] block">壓縮強度預設</label>
                <select 
                  v-model="compressPdfParams.preset"
                  class="w-full px-3 py-2 text-sm font-bold bg-[#F0F4F8] border-[2px] border-[#2C3E50] rounded-xl focus:outline-none focus:ring-2 focus:ring-[#48DBFB]"
                >
                  <option value="auto">🔥 自動逼近目標大小 (推薦)</option>
                  <option value="extreme">💀 毀滅級畫質 (60 DPI / 畫質 12)</option>
                  <option value="strong">⚡ 強力壓縮 (75 DPI / 畫質 20)</option>
                  <option value="medium">⚖️ 平衡壓縮 (95 DPI / 畫質 30)</option>
                  <option value="custom">🛠️ 手動自訂 DPI 與畫質</option>
                </select>
              </div>

              <div v-if="compressPdfParams.preset === 'auto'" class="space-y-1.5">
                <label class="text-xs font-black text-[#2C3E50] block">目標檔案上限 (MB)</label>
                <input 
                  v-model.number="compressPdfParams.targetMb"
                  type="number"
                  min="0.5"
                  max="500"
                  step="0.5"
                  class="w-full px-3 py-2 text-sm font-bold bg-[#F0F4F8] border-[2px] border-[#2C3E50] rounded-xl focus:outline-none focus:ring-2 focus:ring-[#48DBFB]"
                />
              </div>

              <div v-if="compressPdfParams.preset === 'custom'" class="grid grid-cols-2 gap-3">
                <div class="space-y-1">
                  <label class="text-xs font-black text-[#2C3E50] block">解析度 (DPI)</label>
                  <input 
                    v-model.number="compressPdfParams.dpi"
                    type="number"
                    min="40"
                    max="200"
                    class="w-full px-3 py-2 text-sm font-bold bg-[#F0F4F8] border-[2px] border-[#2C3E50] rounded-xl focus:outline-none focus:ring-2 focus:ring-[#48DBFB]"
                  />
                </div>
                <div class="space-y-1">
                  <label class="text-xs font-black text-[#2C3E50] block">畫質 (5~95)</label>
                  <input 
                    v-model.number="compressPdfParams.quality"
                    type="number"
                    min="5"
                    max="95"
                    class="w-full px-3 py-2 text-sm font-bold bg-[#F0F4F8] border-[2px] border-[#2C3E50] rounded-xl focus:outline-none focus:ring-2 focus:ring-[#48DBFB]"
                  />
                </div>
              </div>

              <label class="flex items-start space-x-2.5 cursor-pointer text-xs font-bold text-gray-600 pt-1">
                <input 
                  type="checkbox" 
                  v-model="compressPdfParams.keepColor"
                  class="mt-0.5 w-4 h-4 text-[#FF6B6B] rounded border-[#2C3E50]"
                />
                <span>保留原始彩色（取消則轉為柔和灰階，體積更小）</span>
              </label>
            </div>

            <!-- 6. 照片批次極限壓縮設定選項 -->
            <div v-else-if="currentToolId === 'compress_images'" class="space-y-4 pt-4 border-t-[2px] border-slate-100">
              <div class="space-y-1.5">
                <label class="text-xs font-black text-[#2C3E50] block">最大長邊限制 (px)</label>
                <input 
                  v-model.number="compressImgParams.maxDimension"
                  type="number"
                  min="300"
                  max="4000"
                  step="64"
                  class="w-full px-3 py-2 text-sm font-bold bg-[#F0F4F8] border-[2px] border-[#2C3E50] rounded-xl focus:outline-none focus:ring-2 focus:ring-[#10AC84]"
                />
              </div>

              <div class="space-y-1.5">
                <div class="flex justify-between text-xs font-black text-[#2C3E50]">
                  <span>壓縮畫質</span>
                  <span class="text-[#10AC84]">{{ compressImgParams.quality }}</span>
                </div>
                <input 
                  v-model.number="compressImgParams.quality"
                  type="range"
                  min="5"
                  max="95"
                  class="w-full accent-[#10AC84] cursor-pointer"
                />
              </div>

              <div class="space-y-1.5">
                <label class="text-xs font-black text-[#2C3E50] block">輸出格式</label>
                <div class="grid grid-cols-2 gap-2">
                  <button
                    v-for="fmt in ['JPEG', 'WebP']"
                    :key="fmt"
                    type="button"
                    @click="compressImgParams.outFormat = fmt"
                    :class="[
                      'py-2 rounded-xl text-xs font-black border-[2px] border-[#2C3E50] cursor-pointer transition-all',
                      compressImgParams.outFormat === fmt ? 'bg-[#1DD1A1] text-white shadow-[2px_2px_0px_#2C3E50]' : 'bg-[#F0F4F8] text-gray-500'
                    ]"
                  >
                    {{ fmt }}
                  </button>
                </div>
              </div>
            </div>

            <!-- 7. HEIC 轉 JPG 設定選項 -->
            <div v-else-if="currentToolId === 'heic_to_jpg'" class="space-y-4 pt-4 border-t-[2px] border-slate-100">
              <div class="space-y-1.5">
                <div class="flex justify-between text-xs font-black text-[#2C3E50]">
                  <span>輸出 JPG 畫質</span>
                  <span class="text-[#FF9F43]">{{ heicParams.quality }}</span>
                </div>
                <input 
                  v-model.number="heicParams.quality"
                  type="range"
                  min="60"
                  max="100"
                  class="w-full accent-[#FF9F43] cursor-pointer"
                />
              </div>
              <p class="text-[11px] font-bold text-gray-400">保持原始解析度並自動修正直拍旋轉方向；多張自動打包 ZIP 📦</p>
            </div>

            <!-- 檔案統計與即時容量條 -->
            <div class="bg-[#FFF9E6] p-4 rounded-2xl border-[2px] border-[#2C3E50] space-y-3 text-xs font-bold text-gray-500">
              <div class="flex justify-between">
                <span>檔案數量:</span>
                <span class="font-black text-[#2C3E50]">
                  {{ files.length }} 個
                  <span v-if="isImageBatchTool" class="text-gray-400">/ {{ MAX_IMAGE_COUNT }}</span>
                </span>
              </div>
              <div class="flex justify-between">
                <span>合計大小:</span>
                <span class="font-black text-[#2C3E50]">
                  {{ formatSize(totalBytes) }}
                  <span v-if="isImageBatchTool" class="text-gray-400">/ 50 MB</span>
                </span>
              </div>

              <div v-if="isImageBatchTool" class="space-y-1 pt-1">
                <div class="w-full bg-white h-2.5 rounded-full border-[2px] border-[#2C3E50] overflow-hidden">
                  <div 
                    :class="['h-full transition-all duration-300', quotaPercent > 85 ? 'bg-[#FF6B6B]' : quotaPercent > 60 ? 'bg-[#FECA57]' : 'bg-[#1DD1A1]']"
                    :style="{ width: `${Math.min(100, quotaPercent)}%` }"
                  ></div>
                </div>
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

      <!-- ================= 視圖 3：升級版成果摘要頁 ================= -->
      <section v-else-if="currentStep === 'success'" class="flex-1 flex items-center justify-center p-6 relative z-10 min-h-[60vh]">
        <div class="max-w-md w-full bg-white p-8 sm:p-10 rounded-[2rem] border-[4px] border-[#2C3E50] shadow-[8px_8px_0px_#2C3E50] text-center space-y-6">
          <div class="w-20 h-20 bg-[#1DD1A1] text-white rounded-2xl flex items-center justify-center text-4xl mx-auto font-black border-[4px] border-[#2C3E50] shadow-[4px_4px_0px_#2C3E50] rotate-3">
            ✓
          </div>

          <div class="space-y-1.5">
            <h2 class="text-3xl font-black text-[#2C3E50]">饅頭出爐囉！ 🥟</h2>
            <p class="text-sm font-bold text-gray-500 break-all">{{ downloadFilename }}</p>
          </div>

          <div v-if="resultStats.originalBytes > 0" class="bg-[#FFF9E6] p-4 rounded-2xl border-[2px] border-[#2C3E50] space-y-2 text-xs font-bold">
            <div class="flex items-center justify-between text-gray-500">
              <span>原始大小</span>
              <span class="font-black text-[#2C3E50]">{{ formatSize(resultStats.originalBytes) }}</span>
            </div>
            <div class="flex items-center justify-between text-gray-500">
              <span>處理後大小</span>
              <span class="font-black text-[#2C3E50]">{{ formatSize(resultStats.outputBytes) }}</span>
            </div>
            <div v-if="savedPercent > 0" class="pt-2 border-t-[2px] border-dashed border-[#E5D9B6] text-[#0F766E] font-black text-sm">
              🎉 成功瘦身 {{ savedPercent }}%（省下 {{ formatSize(resultStats.originalBytes - resultStats.outputBytes) }}）
            </div>
          </div>

          <a :href="downloadUrl" :download="downloadFilename" class="cartoon-btn block w-full py-4 rounded-2xl bg-[#FECA57] text-[#2C3E50] border-[3px] border-[#2C3E50] shadow-[4px_4px_0px_#2C3E50] font-black text-lg transition-all cursor-pointer">
            📥 立即下載檔案
          </a>

          <div class="pt-3 flex items-center justify-between text-xs font-black border-t-[2px] border-slate-100">
            <button @click="selectTool(currentToolId)" class="text-[#FF6B6B] hover:underline cursor-pointer">
              ↻ 再處理一批
            </button>
            <button @click="goToHome" class="text-gray-400 hover:text-[#2C3E50] cursor-pointer">
              ← 返回大廳
            </button>
          </div>
          <p class="text-[11px] font-bold text-gray-400">🔥 暫存檔案將於 30 分鐘後自動銷毀</p>
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
        
        <button 
          @click="closeFeedbackModal"
          class="absolute top-5 right-5 w-8 h-8 rounded-full bg-white border-[2px] border-[#2C3E50] text-[#2C3E50] hover:bg-[#FF6B6B] hover:text-white flex items-center justify-center text-sm font-black transition-colors shadow-[2px_2px_0px_#2C3E50] cursor-pointer"
        >
          ✕
        </button>

        <div class="space-y-1">
          <div class="flex items-center gap-2">
            <span class="text-2xl">📮</span>
            <h3 class="text-2xl font-black text-[#2C3E50]">問題回報與建議</h3>
          </div>
          <p class="text-xs font-bold text-gray-400">有任何 Bug 或轉檔問題？送出後會直接寄到作者信箱！</p>
        </div>

        <form @submit.prevent="submitFeedback" class="space-y-4 pt-1">
          <div class="space-y-1">
            <label class="text-xs font-black text-[#2C3E50] block">您的 Email <span class="text-gray-400 font-bold">(選填，若需回覆請填)</span></label>
            <input 
              v-model="feedbackForm.email"
              type="email" 
              placeholder="example@gmail.com"
              class="w-full px-3.5 py-2 text-sm font-bold bg-[#F0F4F8] border-[2px] border-[#2C3E50] rounded-xl focus:outline-none focus:ring-2 focus:ring-[#FECA57]"
            />
          </div>

          <div class="space-y-1">
            <label class="text-xs font-black text-[#2C3E50] block">問題類型</label>
            <select 
              v-model="feedbackForm.type"
              class="w-full px-3.5 py-2 text-sm font-bold bg-[#F0F4F8] border-[2px] border-[#2C3E50] rounded-xl focus:outline-none focus:ring-2 focus:ring-[#FECA57]"
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
              class="w-full px-3.5 py-2 text-sm font-bold bg-[#F0F4F8] border-[2px] border-[#2C3E50] rounded-xl focus:outline-none focus:ring-2 focus:ring-[#FECA57] resize-none"
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
      © 黑糖饅頭很好吃 · 100% 免費且易於使用的線上 PDF 與照片工具 🥟
    </footer>

  </div>
</template>

<script setup>
import { ref, computed, h } from 'vue';
import * as pdfjsLib from 'pdfjs-dist';

pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';

const MAX_IMAGE_COUNT = 20;
const MAX_IMAGE_BYTES = 50 * 1024 * 1024; // 50 MB

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
const resultStats = ref({ originalBytes: 0, outputBytes: 0 });

// ================= 拖曳排序狀態 =================
const dragStartIndex = ref(null);
const dragOverIndex = ref(null);

const onDragStart = (idx) => {
  dragStartIndex.value = idx;
};

const onDropReorder = (targetIdx) => {
  if (dragStartIndex.value === null || dragStartIndex.value === targetIdx) {
    dragOverIndex.value = null;
    return;
  }
  const moved = files.value.splice(dragStartIndex.value, 1)[0];
  files.value.splice(targetIdx, 0, moved);
  dragStartIndex.value = null;
  dragOverIndex.value = null;
};

// ================= Toast 通知系統 =================
const toast = ref({ show: false, message: '', type: 'error' });
let toastTimer = null;

const showToast = (message, type = 'error') => {
  toast.value = { show: true, message, type };
  if (toastTimer) clearTimeout(toastTimer);
  toastTimer = setTimeout(() => {
    toast.value.show = false;
  }, 3600);
};

// ================= 拆分預覽 & 旋轉刪頁整理狀態 =================
const splitPages = ref([]);
const selectedPages = ref(new Set());
const isRenderingPages = ref(false);

const splitParams = ref({
  mode: 'ranges',
  rangesStr: '1',
  chunkSize: 2
});

const organizePages = ref([]);
const initialOrganizeCount = ref(0);

const rotateOrganizePage = (idx, delta) => {
  const target = organizePages.value[idx];
  if (target) {
    target.rotate = (target.rotate + delta + 360) % 360;
  }
};

const rotateAllOrganizePages = (delta) => {
  organizePages.value.forEach(p => {
    p.rotate = (p.rotate + delta + 360) % 360;
  });
};

const moveOrganizePage = (idx, offset) => {
  const targetIdx = idx + offset;
  if (targetIdx < 0 || targetIdx >= organizePages.value.length) return;
  const moved = organizePages.value.splice(idx, 1)[0];
  organizePages.value.splice(targetIdx, 0, moved);
};

const removeOrganizePage = (idx) => {
  if (organizePages.value.length <= 1) {
    showToast('至少要保留 1 頁 PDF 才能輸出喔！');
    return;
  }
  organizePages.value.splice(idx, 1);
};

const resetOrganizePages = () => {
  const total = initialOrganizeCount.value;
  if (!total) return;
  const thumbMap = new Map(organizePages.value.map(p => [p.pageNum, p.thumbnail]));
  organizePages.value = Array.from({ length: total }, (_, i) => ({
    uid: `p_${i + 1}_${Date.now()}`,
    pageNum: i + 1,
    rotate: 0,
    thumbnail: thumbMap.get(i + 1) || null
  }));
};

// ================= 壓縮 / HEIC / 加密 / A4 排版參數 =================
const compressPdfParams = ref({
  preset: 'auto',
  targetMb: 4.5,
  dpi: 75,
  quality: 20,
  keepColor: true
});

const compressImgParams = ref({
  maxDimension: 1024,
  quality: 25,
  outFormat: 'JPEG'
});

const heicParams = ref({
  quality: 92
});

const securityParams = ref({
  action: 'encrypt',
  password: '',
  showPassword: false
});

const a4Params = ref({
  layout: '2_up',
  orientation: 'portrait'
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

const togglePageSelection = (pageNum) => {
  if (selectedPages.value.has(pageNum)) {
    selectedPages.value.delete(pageNum);
  } else {
    selectedPages.value.add(pageNum);
  }
  splitParams.value.mode = 'ranges';
  splitParams.value.rangesStr = numbersToRanges(Array.from(selectedPages.value));
};

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

const onRangesInput = () => {
  if (splitPages.value.length > 0) {
    selectedPages.value = rangesToNumbers(splitParams.value.rangesStr, splitPages.value.length);
  }
};

// ================= 檔案上傳與解析處理 =================
const isImageBatchTool = computed(() => {
  return ['compress_images', 'heic_to_jpg', 'images_to_a4_pdf'].includes(currentToolId.value);
});

const appendFiles = async (fileList) => {
  const incoming = Array.from(fileList || []);
  if (incoming.length === 0) return;

  if (isImageBatchTool.value) {
    if (files.value.length + incoming.length > MAX_IMAGE_COUNT) {
      showToast(`單次最多僅支援上傳 ${MAX_IMAGE_COUNT} 張照片，請分批處理！`);
      return;
    }
    const incomingBytes = incoming.reduce((acc, f) => acc + f.size, 0);
    if (totalBytes.value + incomingBytes > MAX_IMAGE_BYTES) {
      showToast('單次上傳照片總大小不可超過 50 MB，請分批處理！');
      return;
    }
  }

  for (const f of incoming) {
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

    if (f.type.startsWith('image/') && ext !== 'heic' && ext !== 'heif') {
      item.thumbnail = URL.createObjectURL(f);
    }

    if (ext === 'pdf') {
      try {
        const arrayBuffer = await f.arrayBuffer();
        const pdfDoc = await pdfjsLib.getDocument({ data: arrayBuffer }).promise;
        item.pages = pdfDoc.numPages;
        item.thumbnail = await renderPageThumbnail(pdfDoc, 1, 160);

        if (currentToolId.value === 'split_pdf') {
          files.value = [item];
          splitPages.value = [];
          selectedPages.value = new Set([1]);
          splitParams.value.rangesStr = '1';
          isRenderingPages.value = true;

          for (let i = 1; i <= pdfDoc.numPages; i++) {
            splitPages.value.push({ pageNum: i, thumbnail: null });
          }

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

        if (currentToolId.value === 'organize_pdf') {
          files.value = [item];
          organizePages.value = [];
          initialOrganizeCount.value = pdfDoc.numPages;
          isRenderingPages.value = true;

          for (let i = 1; i <= pdfDoc.numPages; i++) {
            organizePages.value.push({
              uid: `p_${i}_${Date.now()}`,
              pageNum: i,
              rotate: 0,
              thumbnail: null
            });
          }

          (async () => {
            for (let i = 1; i <= pdfDoc.numPages; i++) {
              const thumb = await renderPageThumbnail(pdfDoc, i, 160);
              const target = organizePages.value.find(p => p.pageNum === i);
              if (target) target.thumbnail = thumb;
            }
            isRenderingPages.value = false;
          })();

          return;
        }
      } catch (err) {
        console.error('PDF 解析失敗（可能已加密）:', err);
      }
    }

    files.value.push(item);
  }
};

const categories = [
  { id: 'all', name: '全部' },
  { id: 'organize', name: '整理 PDF' },
  { id: 'optimize', name: '優化壓縮' },
  { id: 'convert', name: '格式轉換' },
  { id: 'security', name: '安全加密' }
];

const makeIcon = (pathD, textBadge = null) => {
  return {
    render() {
      if (textBadge) {
        return h('span', { class: 'font-black text-sm tracking-tight' }, textBadge);
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
    desc: '合併多個 PDF 文檔，拖曳卡片即可自由排列順序！',
    badges: ['PDF'],
    iconBg: 'bg-[#FF6B6B]',
    iconSvg: makeIcon('M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z'),
    accept: '.pdf',
    buttonText: '選擇多個 PDF 檔案',
    actionText: '合併 PDF →'
  },
  {
    id: 'split_pdf',
    category: 'organize',
    title: '拆分PDF',
    desc: '視覺化點選想留下的頁面，或全部拆為獨立單頁。',
    badges: ['PDF'],
    iconBg: 'bg-[#FECA57]',
    iconSvg: makeIcon('M9.64 7.64c.23-.5.36-1.05.36-1.64 0-2.21-1.79-4-4-4S2 3.79 2 6s1.79 4 4 4c.59 0 1.14-.13 1.64-.36L10 12l-2.36 2.36C7.14 14.13 6.59 14 6 14c-2.21 0-4 1.79-4 4s1.79 4 4 4 4-1.79 4-4c0-.59-.13-1.14-.36-1.64L12 14l7 7h3v-1L9.64 7.64zM6 8c-1.1 0-2-.9-2-2s.9-2 2-2 2 .9 2 2-.9 2-2 2zm0 12c-1.1 0-2-.9-2-2s.9-2 2-2 2 .9 2 2-.9 2-2 2zm6-7.5c-.28 0-.5-.22-.5-.5s.22-.5.5-.5.5.22.5.5-.22.5-.5.5zM19 3l-6 6 2 2 7-7V3h-3z'),
    accept: '.pdf',
    buttonText: '選擇 PDF 檔案',
    actionText: '拆分 PDF →'
  },
  {
    id: 'organize_pdf',
    category: 'organize',
    title: 'PDF 旋轉刪頁',
    desc: '單頁旋轉 90°、刪除空白頁、調整前後頁序一氣呵成！',
    badges: ['PDF'],
    iconBg: 'bg-[#FF9F43]',
    iconSvg: makeIcon('M12 5V1L7 6l5 5V7c3.31 0 6 2.69 6 6s-2.69 6-6 6-6-2.69-6-6H4c0 4.42 3.58 8 8 8s8-3.58 8-8-3.58-8-8-8z'),
    accept: '.pdf',
    buttonText: '選擇 PDF 檔案',
    actionText: '儲存整理結果 →'
  },
  {
    id: 'compress_pdf',
    category: 'optimize',
    title: 'PDF 極限壓縮',
    desc: '保留原檔外觀與印章細節，自動逼近目標 MB 或手動壓到最小。',
    badges: ['PDF'],
    iconBg: 'bg-[#48DBFB]',
    iconSvg: makeIcon('M19 12h-2v3h-3v2h5v-5zM7 9h3V7H5v5h2V9zm14-6H3c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h18c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16.01H3V4.99h18v14.02z'),
    accept: '.pdf',
    buttonText: '選擇 PDF 檔案',
    actionText: '開始極限壓縮 →'
  },
  {
    id: 'compress_images',
    category: 'optimize',
    title: '照片批次壓縮',
    desc: '多張照片一次縮放瘦身成 JPEG 或 WebP（限 20 張 / 50 MB）。',
    badges: ['JPG', 'PNG', 'HEIC'],
    iconBg: 'bg-[#10AC84]',
    iconSvg: makeIcon('M21 19V5c0-1.1-.9-2-2-2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2zM8.5 13.5l2.5 3.01L14.5 12l4.5 6H5l3.5-4.5z'),
    accept: '.jpg,.jpeg,.png,.webp,.bmp,.heic,.heif',
    buttonText: '選擇多張照片',
    actionText: '批次極限壓縮 →'
  },
  {
    id: 'images_to_a4_pdf',
    category: 'convert',
    title: '照片排版 A4',
    desc: '多張照片自動依每頁 1 / 2 / 4 張整齊排進 A4 PDF（限 20 張）。',
    badges: ['JPG', 'PNG', 'HEIC'],
    iconBg: 'bg-[#EE5253]',
    iconSvg: makeIcon('M4 4h7v7H4V4zm9 0h7v7h-7V4zM4 13h7v7H4v-7zm9 0h7v7h-7v-7z'),
    accept: '.jpg,.jpeg,.png,.webp,.bmp,.heic,.heif',
    buttonText: '選擇多張照片',
    actionText: '產生 A4 PDF →'
  },
  {
    id: 'heic_to_jpg',
    category: 'convert',
    title: 'HEIC 轉 JPG',
    desc: '將蘋果手機的 HEIC 照片快速轉成通用 JPG 並自動轉正。',
    badges: ['HEIC', 'HEIF'],
    iconBg: 'bg-[#FF9F43]',
    iconSvg: makeIcon(null, 'HEIC'),
    accept: '.heic,.heif',
    buttonText: '選擇 HEIC 照片',
    actionText: '轉換為 JPG →'
  },
  {
    id: 'pdf_to_word',
    category: 'convert',
    title: 'PDF 轉 Word',
    desc: '輕鬆將 PDF 轉為可編輯的 DOCX 文檔。',
    badges: ['PDF', 'DOCX'],
    iconBg: 'bg-[#1DD1A1]',
    iconSvg: makeIcon(null, 'W'),
    accept: '.pdf',
    buttonText: '選擇 PDF 檔案',
    actionText: '轉換為 Word →'
  },
  {
    id: 'word_to_pdf',
    category: 'convert',
    title: 'Word 轉 PDF',
    desc: '將 DOC 或 DOCX 轉換為 PDF 文檔，保持排版品質。',
    badges: ['DOCX', 'DOC'],
    iconBg: 'bg-[#54A0FF]',
    iconSvg: makeIcon(null, 'W'),
    accept: '.docx,.doc',
    buttonText: '選擇 Word 文件',
    actionText: '轉換為 PDF →'
  },
  {
    id: 'pdf_to_jpg',
    category: 'convert',
    title: 'PDF轉JPG',
    desc: '將 PDF 每一頁快速轉存為高畫質 JPG 圖片。',
    badges: ['PDF', 'JPG'],
    iconBg: 'bg-[#FECA57]',
    iconSvg: makeIcon('M21 19V5c0-1.1-.9-2-2-2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2zM8.5 13.5l2.5 3.01L14.5 12l4.5 6H5l3.5-4.5z'),
    accept: '.pdf',
    buttonText: '選擇 PDF 檔案',
    actionText: '轉換為 JPG →'
  },
  {
    id: 'jpg_to_pdf',
    category: 'convert',
    title: 'JPG轉PDF',
    desc: '將多張圖片依序合併轉換為一份 PDF 文件。',
    badges: ['JPG', 'PNG'],
    iconBg: 'bg-[#FF6B6B]',
    iconSvg: makeIcon('M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z'),
    accept: '.jpg,.jpeg,.png',
    buttonText: '選擇多張圖片',
    actionText: '合併為 PDF →'
  },
  {
    id: 'security_pdf',
    category: 'security',
    title: 'PDF 加密 / 解鎖',
    desc: '幫重要 PDF 設定開啟密碼，或移除已知密碼的 PDF 限制。',
    badges: ['PDF', 'AES-256'],
    iconBg: 'bg-[#5F27CD]',
    iconSvg: makeIcon('M18 8h-1V6c0-2.76-2.24-5-5-5S7 3.24 7 6v2H6c-1.1 0-2 .9-2 2v10c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V10c0-1.1-.9-2-2-2zm-6 9c-1.1 0-2-.9-2-2s.9-2 2-2 2 .9 2 2-.9 2-2 2zm3.1-9H8.9V6c0-1.71 1.39-3.1 3.1-3.1 1.71 0 3.1 1.39 3.1 3.1v2z'),
    accept: '.pdf',
    buttonText: '選擇 PDF 檔案',
    actionText: '執行安全處理 →'
  }
];

const getToolTitle = (id) => tools.find(t => t.id === id)?.title || '';

const getCategoryCount = (catId) => {
  if (catId === 'all') return tools.length;
  return tools.filter(t => t.category === catId).length;
};

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

const quotaPercent = computed(() => {
  const countPct = (files.value.length / MAX_IMAGE_COUNT) * 100;
  const bytesPct = (totalBytes.value / MAX_IMAGE_BYTES) * 100;
  return Math.max(countPct, bytesPct);
});

const savedPercent = computed(() => {
  const { originalBytes, outputBytes } = resultStats.value;
  if (!originalBytes || !outputBytes || outputBytes >= originalBytes) return 0;
  return (((originalBytes - outputBytes) / originalBytes) * 100).toFixed(1);
});

const selectTool = (toolId) => {
  currentToolId.value = toolId;
  files.value = [];
  splitPages.value = [];
  organizePages.value = [];
  selectedPages.value.clear();
  currentStep.value = 'workspace';
};

const goToHome = () => {
  files.value = [];
  splitPages.value = [];
  organizePages.value = [];
  selectedPages.value.clear();
  currentStep.value = 'hub';
};

const clearWorkspace = () => {
  files.value = [];
  splitPages.value = [];
  organizePages.value = [];
  selectedPages.value.clear();
};

const triggerFileInput = () => {
  if (fileInputRef.value) {
    fileInputRef.value.click();
  }
};

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
  return (b / 1048576).toFixed(2) + ' MB';
};

const executeTool = async () => {
  if (files.value.length === 0) return;

  if (currentToolId.value === 'split_pdf' && splitParams.value.mode === 'ranges' && !splitParams.value.rangesStr.trim()) {
    showToast('請至少勾選一頁或輸入拆分範圍！');
    return;
  }
  if (currentToolId.value === 'organize_pdf' && organizePages.value.length === 0) {
    showToast('請至少保留 1 頁 PDF！');
    return;
  }
  if (currentToolId.value === 'security_pdf' && !securityParams.value.password.trim()) {
    showToast('請輸入 PDF 密碼！');
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
  } else if (currentToolId.value === 'organize_pdf') {
    const ops = organizePages.value.map(p => ({ page: p.pageNum, rotate: p.rotate }));
    formData.append('page_ops', JSON.stringify(ops));
  } else if (currentToolId.value === 'security_pdf') {
    formData.append('security_action', securityParams.value.action);
    formData.append('pdf_password', securityParams.value.password);
  } else if (currentToolId.value === 'images_to_a4_pdf') {
    formData.append('a4_layout', a4Params.value.layout);
    formData.append('a4_orientation', a4Params.value.orientation);
  } else if (currentToolId.value === 'compress_pdf') {
    formData.append('compress_preset', compressPdfParams.value.preset);
    formData.append('target_mb', compressPdfParams.value.targetMb);
    formData.append('dpi', compressPdfParams.value.dpi);
    formData.append('quality', compressPdfParams.value.quality);
    formData.append('keep_color', compressPdfParams.value.keepColor);
  } else if (currentToolId.value === 'compress_images') {
    formData.append('max_dimension', compressImgParams.value.maxDimension);
    formData.append('quality', compressImgParams.value.quality);
    formData.append('out_format', compressImgParams.value.outFormat);
  } else if (currentToolId.value === 'heic_to_jpg') {
    formData.append('heic_quality', heicParams.value.quality);
  }

  try {
    progress.value = 65;
    progressText.value = '正在努力加熱中... ♨️';

    const res = await fetch('/api/convert', { method: 'POST', body: formData });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || '處理失敗');
    }

    const data = await res.json();
    progress.value = 100;
    downloadUrl.value = data.download_url;
    downloadFilename.value = data.filename;
    resultStats.value = {
      originalBytes: data.original_bytes || totalBytes.value,
      outputBytes: data.output_bytes || 0
    };
    currentStep.value = 'success';
  } catch (err) {
    showToast(`執行失敗：${err.message}`);
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
  background-size: 28px 28px;
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
  transform: translate(3px, 3px);
  box-shadow: 1px 1px 0px #2C3E50 !important;
}

.cartoon-card {
  transition: all 0.2s cubic-bezier(0.34, 1.56, 0.64, 1);
}
.cartoon-card:hover {
  transform: translateY(-4px);
  box-shadow: 7px 8px 0px #2C3E50 !important;
}
.cartoon-card:active {
  transform: translateY(2px);
  box-shadow: 2px 2px 0px #2C3E50 !important;
}

.toast-enter-active,
.toast-leave-active {
  transition: all 0.25s ease;
}
.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateY(-12px);
}
</style>
