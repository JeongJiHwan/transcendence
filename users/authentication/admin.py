from django.contrib import admin
from django.contrib.sessions.models import Session

@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ['session_key', 'expire_date', 'get_session_data']

    def get_session_data(self, obj):
        # 세션 데이터에서 특정 필드를 출력하거나 처리할 수 있는 로직
        return obj.get_decoded()  # 예시로 세션 데이터의 디코딩된 값 반환

    get_session_data.short_description = 'Session Data'