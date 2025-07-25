#!/usr/bin/env python3
"""
Simple localization system for Reporter app
Supports English, Thai, and Chinese UI translations
"""

import yaml
from pathlib import Path

# Translation dictionaries
TRANSLATIONS = {
    'en': {
        # Main UI
        'app_title': 'Reporter - Work Tracker',
        'quick_work_entry': 'Quick Work Entry:',
        'organization': 'Organization:',
        'issue_pr': 'Issue/PR:',
        'select_organization': 'Select organization...',
        'select_issue_pr': 'Select issue/PR...',
        'work_description_placeholder': 'Enter work description... (Press Enter to save)',
        'save_entry': 'Save Entry (Enter)',
        
        # Work Log Panel
        'todays_work_log': "Today's Work Log:",
        'copy_to_clipboard': 'Copy to Clipboard',
        'generate_llm_report': 'Generate LLM Report',
        
        # LLM Panel
        'llm_standup_report': 'LLM Generated Standup Report:',
        'copy_llm_report': 'Copy LLM Report',
        'llm_placeholder': "Click 'Generate LLM Report' to process your work log with AI...",
        
        # Buttons
        'refresh_github_data': 'Refresh GitHub Data',
        'open_context_yml': 'Open context.yml',
        
        # Messages
        'copied': 'Copied',
        'work_log_copied': 'Work log copied to clipboard!',
        'llm_report_copied': 'LLM report copied to clipboard!',
        'success': 'Success',
        'github_data_refreshed': 'GitHub data refreshed successfully!',
        'error': 'Error',
        'empty_entry': 'Empty Entry',
        'enter_work_description': 'Please enter some work description.',
        'no_data': 'No Data',
        'no_worklog_entries': 'No work log entries to process.',
        'processing_llm': '🤖 Processing work log with LLM... This may take a moment...',
        
        # Language Selection
        'language': 'Language',
        'select_language': 'Select Language',
    },
    
    'th': {
        # Main UI
        'app_title': 'Reporter - เครื่องมือติดตามงาน',
        'quick_work_entry': 'บันทึกงานด่วน:',
        'organization': 'องค์กร:',
        'issue_pr': 'Issue/PR:',
        'select_organization': 'เลือกองค์กร...',
        'select_issue_pr': 'เลือก issue/PR...',
        'work_description_placeholder': 'ใส่รายละเอียดงาน... (กด Enter เพื่อบันทึก)',
        'save_entry': 'บันทึก (Enter)',
        
        # Work Log Panel
        'todays_work_log': 'บันทึกงานวันนี้:',
        'copy_to_clipboard': 'คัดลอกไปยังคลิปบอร์ด',
        'generate_llm_report': 'สร้างรายงาน LLM',
        
        # LLM Panel
        'llm_standup_report': 'รายงาน Standup จาก LLM:',
        'copy_llm_report': 'คัดลอกรายงาน LLM',
        'llm_placeholder': "คลิก 'สร้างรายงาน LLM' เพื่อประมวลผลบันทึกงานด้วย AI...",
        
        # Buttons
        'refresh_github_data': 'รีเฟรชข้อมูล GitHub',
        'open_context_yml': 'เปิด context.yml',
        
        # Messages
        'copied': 'คัดลอกแล้ว',
        'work_log_copied': 'คัดลอกบันทึกงานไปยังคลิปบอร์ดแล้ว!',
        'llm_report_copied': 'คัดลอกรายงาน LLM ไปยังคลิปบอร์ดแล้ว!',
        'success': 'สำเร็จ',
        'github_data_refreshed': 'รีเฟรชข้อมูล GitHub สำเร็จแล้ว!',
        'error': 'ข้อผิดพลาด',
        'empty_entry': 'ไม่มีข้อมูล',
        'enter_work_description': 'กรุณาใส่รายละเอียดงาน',
        'no_data': 'ไม่มีข้อมูล',
        'no_worklog_entries': 'ไม่มีบันทึกงานให้ประมวลผล',
        'processing_llm': '🤖 กำลังประมวลผลบันทึกงานด้วย LLM... กรุณารอสักครู่...',
        
        # Language Selection
        'language': 'ภาษา',
        'select_language': 'เลือกภาษา',
    },
    
    'zh': {
        # Main UI
        'app_title': 'Reporter - 工作跟踪器',
        'quick_work_entry': '快速工作记录:',
        'organization': '组织:',
        'issue_pr': 'Issue/PR:',
        'select_organization': '选择组织...',
        'select_issue_pr': '选择 issue/PR...',
        'work_description_placeholder': '输入工作描述... (按 Enter 保存)',
        'save_entry': '保存 (Enter)',
        
        # Work Log Panel
        'todays_work_log': '今日工作日志:',
        'copy_to_clipboard': '复制到剪贴板',
        'generate_llm_report': '生成 LLM 报告',
        
        # LLM Panel
        'llm_standup_report': 'LLM 生成的站会报告:',
        'copy_llm_report': '复制 LLM 报告',
        'llm_placeholder': "点击 '生成 LLM 报告' 用 AI 处理您的工作日志...",
        
        # Buttons
        'refresh_github_data': '刷新 GitHub 数据',
        'open_context_yml': '打开 context.yml',
        
        # Messages
        'copied': '已复制',
        'work_log_copied': '工作日志已复制到剪贴板!',
        'llm_report_copied': 'LLM 报告已复制到剪贴板!',
        'success': '成功',
        'github_data_refreshed': 'GitHub 数据刷新成功!',
        'error': '错误',
        'empty_entry': '空记录',
        'enter_work_description': '请输入工作描述',
        'no_data': '无数据',
        'no_worklog_entries': '没有工作日志可处理',
        'processing_llm': '🤖 正在用 LLM 处理工作日志... 请稍候...',
        
        # Language Selection
        'language': '语言',
        'select_language': '选择语言',
    }
}

def get_language_from_config():
    """Get current language from context.yml"""
    try:
        context_file = Path(__file__).parent.parent / 'context.yml'
        if context_file.exists():
            with open(context_file, 'r') as f:
                data = yaml.safe_load(f) or {}
                ui_config = data.get('ui', {})
                return ui_config.get('language', 'en')
    except Exception as e:
        print(f"Error loading language config: {e}")
    return 'en'

def get_available_languages():
    """Get available languages from context.yml"""
    try:
        context_file = Path(__file__).parent.parent / 'context.yml'
        if context_file.exists():
            with open(context_file, 'r') as f:
                data = yaml.safe_load(f) or {}
                ui_config = data.get('ui', {})
                return ui_config.get('available_languages', {'en': 'English'})
    except Exception as e:
        print(f"Error loading available languages: {e}")
    return {'en': 'English'}

def set_language(language_code):
    """Set language in context.yml"""
    try:
        context_file = Path(__file__).parent.parent / 'context.yml'
        if context_file.exists():
            with open(context_file, 'r') as f:
                data = yaml.safe_load(f) or {}
            
            if 'ui' not in data:
                data['ui'] = {}
            data['ui']['language'] = language_code
            
            with open(context_file, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
            return True
    except Exception as e:
        print(f"Error setting language: {e}")
    return False

def tr(key, language=None):
    """Translate a key to the current or specified language"""
    if language is None:
        language = get_language_from_config()
    
    if language in TRANSLATIONS and key in TRANSLATIONS[language]:
        return TRANSLATIONS[language][key]
    
    # Fallback to English
    if key in TRANSLATIONS['en']:
        return TRANSLATIONS['en'][key]
    
    # Fallback to key itself
    return key

# Convenience function for common usage
def _(key):
    """Short alias for tr() function"""
    return tr(key)

if __name__ == '__main__':
    # Test the localization system
    print("Testing localization system:")
    for lang in ['en', 'th', 'zh']:
        print(f"\n{lang.upper()}:")
        print(f"  App Title: {tr('app_title', lang)}")
        print(f"  Quick Entry: {tr('quick_work_entry', lang)}")
        print(f"  Save Button: {tr('save_entry', lang)}")