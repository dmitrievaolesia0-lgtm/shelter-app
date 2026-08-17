import db_analytics as analytics
import db_birthdays as birthdays

# Импортируем ваши раздельные файлы
import part_1_prepare_data as p1
import part_2_filter_data as p2
import part_3_render_view as p3

def show_admin_panel():
    """Главный диспетчер, связывающий 4 отдельных файла в общую цепочку"""
    # 1. Вызываем первую часть из файла 1
    df, sort_options, selected_sort, selected_districts, view_mode = p1.part_1_prepare_data()
    
    if df is None:
        return
        
    # 2. Передаем данные в файл 2 (фильтрация)
    filtered_df, display_df = p2.part_2_filter_data(df, sort_options, selected_sort, selected_districts)
    
    # 3. Передаем результаты в файл 3 (отрисовка)
    p3.part_3_render_view(view_mode, filtered_df, display_df, df)
    
    # 4. Общие графики внизу страницы
    analytics.render_analytics_charts(display_df)
    birthdays.render_birthday_alert(df)
