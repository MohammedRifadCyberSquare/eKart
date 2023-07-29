from eKart_admin.models import Category

def get_category_list(self):
    category_list = Category.objects.all()

    return dict(category_list = category_list)