import json
import os

class TenantManager:
    def __init__(self, tenants_file_path=None):
        """مدیریت اطلاعات مستاجرها"""
        if tenants_file_path is None:
            # مسیر پیش‌فرض فایل تنظیمات مستاجرها
            self.tenants_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'tenants.json')
        else:
            self.tenants_file_path = tenants_file_path
        
        self.tenants = {}
        self.load_tenants()
    
    def load_tenants(self):
        """بارگذاری اطلاعات مستاجرها از فایل JSON"""
        try:
            with open(self.tenants_file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                
                # ذخیره اطلاعات مستاجرها با کلید tenant_id
                for tenant in data.get('tenants', []):
                    tenant_id = tenant.get('id')
                    if tenant_id:
                        self.tenants[tenant_id] = tenant
                
                print(f"مستاجرها با موفقیت بارگذاری شدند: {len(self.tenants)} مستاجر یافت شد.")
        except Exception as e:
            print(f"خطا در بارگذاری فایل مستاجرها: {str(e)}")
    
    def get_tenant(self, tenant_id):
        """دریافت اطلاعات یک مستاجر با شناسه"""
        return self.tenants.get(tenant_id)
    
    def verify_api_key(self, tenant_id, api_key):
        """تأیید کلید API مستاجر"""
        tenant = self.get_tenant(tenant_id)
        if tenant and tenant.get('api_key') == api_key:
            return True
        return False
    
    def get_all_tenants(self):
        """دریافت لیست تمام مستاجرها"""
        return list(self.tenants.values())
    
    def get_tenant_setting(self, tenant_id, setting_key, default_value=None):
        """دریافت تنظیمات خاص یک مستاجر"""
        tenant = self.get_tenant(tenant_id)
        if tenant and 'settings' in tenant:
            return tenant['settings'].get(setting_key, default_value)
        return default_value