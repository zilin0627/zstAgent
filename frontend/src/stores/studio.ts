import { defineStore } from 'pinia';
import { requestStudioGenerate } from '@/services/api';

export type StudioDirection = '海报视觉' | '丝巾设计' | '课程工作坊' | '品牌包装';
export type StudioTone = '传统庄重' | '轻盈现代' | '几何理性' | '节庆热烈';

export const useStudioStore = defineStore('studio', {
  state: () => ({
    pattern: '龙纹',
    theme: '围绕龙纹展开当代转化',
    direction: '海报视觉' as StudioDirection,
    tone: '传统庄重' as StudioTone,
    note: '希望用于侗绣主题展主视觉，突出守护感、中心构图与礼仪气质。',
    allowWeb: true,
    generationMode: '快速模式（直连知识库）',
    loading: false,
    generated: false,
    citations: [] as unknown[],
    result: {
      title: '',
      positioning: '',
      copywriting: '',
      suggestions: [] as string[],
      rawText: '',
    },
  }),
  actions: {
    async generateProposal() {
      this.loading = true;
      try {
        const response = await requestStudioGenerate({
          pattern_name: this.pattern,
          theme: this.theme,
          target: this.direction,
          tone: this.tone,
          extra: this.note,
          allow_web: this.allowWeb,
          generation_mode: this.generationMode,
        });
        this.result.rawText = response.answer || '';
        this.result.title = this.pattern;
        this.result.positioning = response.answer || '';
        this.result.copywriting = response.answer || '';
        this.result.suggestions = [];
        this.citations = Array.isArray(response.citations)
          ? response.citations
          : response.citations?.citations || [];
        this.generated = true;
      } catch (error) {
        const message = error instanceof Error ? error.message : '设计提案生成失败';
        this.result.rawText = message;
        this.result.title = this.pattern;
        this.result.positioning = message;
        this.result.copywriting = message;
        this.result.suggestions = [];
        this.citations = [];
        this.generated = true;
      } finally {
        this.loading = false;
      }
    },
  },
});
