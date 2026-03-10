class ErrorCollector:
    def __init__(self):
        self.errors = []

    def add_error(self, category, row, column, value, msg_en):
        self.errors.append({
            'category': category, 'row': row, 'column': column, 
            'value': value, 'en': msg_en
        })

    def has_errors(self):
        return len(self.errors) > 0

    def get_report(self):
        if not self.errors: return ""
        
        report = f"{'ROW':<6} | {'CATEGORY':<12} | {'COLUMN':<18} | {'VALUE':<20} | {'MESSAGE'}\n"
        report += "-" * 100 + "\n"
        
        for e in sorted(self.errors, key=lambda x: x['row']):
            report += f"{e['row']:<6} | {e['category']:<12} | {str(e['column'])[:16]:<18} | {str(e['value'])[:18]:<20} | {e['en']}\n"
        
        return report