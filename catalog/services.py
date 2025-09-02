from catalog.models import Product, Category

class CategoryService:
    @staticmethod
    def get_products_by_category(category_id, raise_exception=False):
        """
        Возвращает список продуктов по ID категории.

        :param category_id: ID категории
        :param raise_exception: если True — выбрасывает исключение, если категории нет
        :return: QuerySet<Product>
        """
        qs = Product.objects.filter(category_id=category_id)

        if raise_exception and not Category.objects.filter(id=category_id).exists():
            raise Category.DoesNotExist(f"Category with id={category_id} does not exist")

        return qs
