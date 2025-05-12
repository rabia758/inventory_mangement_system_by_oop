import json
import abc
from datetime import datetime, date
from typing import Dict, List, Union, Type, Optional

# Custom Exceptions
class InventoryError(Exception):
    """Base exception for inventory-related errors"""
    pass

class InsufficientStockError(InventoryError):
    """Raised when trying to sell more items than available"""
    pass

class DuplicateProductError(InventoryError):
    """Raised when adding a product with a duplicate ID"""
    pass

class InvalidProductDataError(InventoryError):
    """Raised when loading invalid product data"""
    pass

# Abstract Base Class
class Product(abc.ABC):
    def __init__(self, product_id: str, name: str, price: float, quantity_in_stock: int):
        self._product_id = product_id
        self._name = name
        self._price = price
        self._quantity_in_stock = quantity_in_stock
    
    @property
    def product_id(self) -> str:
        return self._product_id
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def price(self) -> float:
        return self._price
    
    @price.setter
    def price(self, new_price: float):
        if new_price <= 0:
            raise ValueError("Price must be positive")
        self._price = new_price
    
    @property
    def quantity_in_stock(self) -> int:
        return self._quantity_in_stock
    
    def restock(self, amount: int) -> None:
        if amount <= 0:
            raise ValueError("Restock amount must be positive")
        self._quantity_in_stock += amount
    
    def sell(self, quantity: int) -> None:
        if quantity <= 0:
            raise ValueError("Sale quantity must be positive")
        if quantity > self._quantity_in_stock:
            raise InsufficientStockError(
                f"Not enough stock. Available: {self._quantity_in_stock}, Requested: {quantity}"
            )
        self._quantity_in_stock -= quantity
    
    def get_total_value(self) -> float:
        return self._price * self._quantity_in_stock
    
    @abc.abstractmethod
    def __str__(self) -> str:
        pass
    
    @abc.abstractmethod
    def to_dict(self) -> Dict:
        """Convert product to dictionary for serialization"""
        pass
    
    @classmethod
    @abc.abstractmethod
    def from_dict(cls, data: Dict) -> 'Product':
        """Create product from dictionary (for deserialization)"""
        pass

# Product Subclasses
class Electronics(Product):
    def __init__(self, product_id: str, name: str, price: float, quantity_in_stock: int, 
                 warranty_years: int, brand: str):
        super().__init__(product_id, name, price, quantity_in_stock)
        self._warranty_years = warranty_years
        self._brand = brand
    
    @property
    def warranty_years(self) -> int:
        return self._warranty_years
    
    @property
    def brand(self) -> str:
        return self._brand
    
    def __str__(self) -> str:
        return (f"Electronics - ID: {self._product_id}, Name: {self._name}, "
                f"Brand: {self._brand}, Price: ${self._price:.2f}, "
                f"Warranty: {self._warranty_years} years, "
                f"Stock: {self._quantity_in_stock}")
    
    def to_dict(self) -> Dict:
        return {
            'type': 'electronics',
            'product_id': self._product_id,
            'name': self._name,
            'price': self._price,
            'quantity_in_stock': self._quantity_in_stock,
            'warranty_years': self._warranty_years,
            'brand': self._brand
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Electronics':
        return cls(
            data['product_id'],
            data['name'],
            data['price'],
            data['quantity_in_stock'],
            data['warranty_years'],
            data['brand']
        )

class Grocery(Product):
    def __init__(self, product_id: str, name: str, price: float, quantity_in_stock: int, 
                 expiry_date: str):
        super().__init__(product_id, name, price, quantity_in_stock)
        self._expiry_date = datetime.strptime(expiry_date, "%Y-%m-%d").date()
    
    @property
    def expiry_date(self) -> date:
        return self._expiry_date
    
    def is_expired(self) -> bool:
        return self._expiry_date < date.today()
    
    def __str__(self) -> str:
        expired = " (EXPIRED)" if self.is_expired() else ""
        return (f"Grocery - ID: {self._product_id}, Name: {self._name}, "
                f"Price: ${self._price:.2f}, Expiry: {self._expiry_date}{expired}, "
                f"Stock: {self._quantity_in_stock}")
    
    def to_dict(self) -> Dict:
        return {
            'type': 'grocery',
            'product_id': self._product_id,
            'name': self._name,
            'price': self._price,
            'quantity_in_stock': self._quantity_in_stock,
            'expiry_date': self._expiry_date.strftime("%Y-%m-%d")
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Grocery':
        return cls(
            data['product_id'],
            data['name'],
            data['price'],
            data['quantity_in_stock'],
            data['expiry_date']
        )

class Clothing(Product):
    def __init__(self, product_id: str, name: str, price: float, quantity_in_stock: int, 
                 size: str, material: str):
        super().__init__(product_id, name, price, quantity_in_stock)
        self._size = size
        self._material = material
    
    @property
    def size(self) -> str:
        return self._size
    
    @property
    def material(self) -> str:
        return self._material
    
    def __str__(self) -> str:
        return (f"Clothing - ID: {self._product_id}, Name: {self._name}, "
                f"Size: {self._size}, Material: {self._material}, "
                f"Price: ${self._price:.2f}, Stock: {self._quantity_in_stock}")
    
    def to_dict(self) -> Dict:
        return {
            'type': 'clothing',
            'product_id': self._product_id,
            'name': self._name,
            'price': self._price,
            'quantity_in_stock': self._quantity_in_stock,
            'size': self._size,
            'material': self._material
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Clothing':
        return cls(
            data['product_id'],
            data['name'],
            data['price'],
            data['quantity_in_stock'],
            data['size'],
            data['material']
        )

# Inventory Class
class Inventory:
    def __init__(self):
        self._products: Dict[str, Product] = {}
    
    def add_product(self, product: Product) -> None:
        if product.product_id in self._products:
            raise DuplicateProductError(f"Product ID {product.product_id} already exists")
        self._products[product.product_id] = product
    
    def remove_product(self, product_id: str) -> None:
        if product_id not in self._products:
            raise KeyError(f"Product ID {product_id} not found")
        del self._products[product_id]
    
    def search_by_name(self, name: str) -> List[Product]:
        return [p for p in self._products.values() if name.lower() in p.name.lower()]
    
    def search_by_type(self, product_type: Type[Product]) -> List[Product]:
        return [p for p in self._products.values() if isinstance(p, product_type)]
    
    def list_all_products(self) -> List[Product]:
        return list(self._products.values())
    
    def sell_product(self, product_id: str, quantity: int) -> None:
        if product_id not in self._products:
            raise KeyError(f"Product ID {product_id} not found")
        self._products[product_id].sell(quantity)
    
    def restock_product(self, product_id: str, quantity: int) -> None:
        if product_id not in self._products:
            raise KeyError(f"Product ID {product_id} not found")
        self._products[product_id].restock(quantity)
    
    def total_inventory_value(self) -> float:
        return sum(p.get_total_value() for p in self._products.values())
    
    def remove_expired_products(self) -> List[Product]:
        expired = []
        for product_id, product in list(self._products.items()):
            if isinstance(product, Grocery) and product.is_expired():
                expired.append(self._products.pop(product_id))
        return expired
    
    def save_to_file(self, filename: str) -> None:
        data = {
            'products': [product.to_dict() for product in self._products.values()]
        }
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)
    
    def load_from_file(self, filename: str) -> None:
        with open(filename, 'r') as f:
            data = json.load(f)
        
        self._products = {}
        product_classes = {
            'electronics': Electronics,
            'grocery': Grocery,
            'clothing': Clothing
        }
        
        for product_data in data['products']:
            try:
                product_type = product_data['type']
                if product_type not in product_classes:
                    raise InvalidProductDataError(f"Unknown product type: {product_type}")
                
                product = product_classes[product_type].from_dict(product_data)
                self.add_product(product)
            except KeyError as e:
                raise InvalidProductDataError(f"Missing required field: {e}")

# CLI Interface
class InventoryCLI:
    def __init__(self):
        self.inventory = Inventory()
    
    def run(self):
        print("Inventory Management System")
        print("--------------------------")
        
        while True:
            print("\nMenu:")
            print("1. Add Product")
            print("2. Sell Product")
            print("3. Search/View Products")
            print("4. Save Inventory")
            print("5. Load Inventory")
            print("6. Remove Expired Groceries")
            print("7. Exit")
            
            choice = input("Enter your choice (1-7): ")
            
            try:
                if choice == '1':
                    self._add_product_menu()
                elif choice == '2':
                    self._sell_product_menu()
                elif choice == '3':
                    self._search_view_menu()
                elif choice == '4':
                    self._save_inventory_menu()
                elif choice == '5':
                    self._load_inventory_menu()
                elif choice == '6':
                    expired = self.inventory.remove_expired_products()
                    print(f"Removed {len(expired)} expired grocery items")
                elif choice == '7':
                    print("Exiting...")
                    break
                else:
                    print("Invalid choice. Please try again.")
            except Exception as e:
                print(f"Error: {e}")
    
    def _add_product_menu(self):
        print("\nAdd Product:")
        print("1. Electronics")
        print("2. Grocery")
        print("3. Clothing")
        print("4. Back to Main Menu")
        
        choice = input("Enter product type (1-4): ")
        if choice == '4':
            return
        
        product_id = input("Enter product ID: ")
        name = input("Enter product name: ")
        price = float(input("Enter price: "))
        quantity = int(input("Enter initial stock quantity: "))
        
        if choice == '1':
            warranty = int(input("Enter warranty years: "))
            brand = input("Enter brand: ")
            product = Electronics(product_id, name, price, quantity, warranty, brand)
        elif choice == '2':
            expiry = input("Enter expiry date (YYYY-MM-DD): ")
            product = Grocery(product_id, name, price, quantity, expiry)
        elif choice == '3':
            size = input("Enter size: ")
            material = input("Enter material: ")
            product = Clothing(product_id, name, price, quantity, size, material)
        else:
            print("Invalid choice")
            return
        
        self.inventory.add_product(product)
        print("Product added successfully!")
    
    def _sell_product_menu(self):
        product_id = input("Enter product ID to sell: ")
        quantity = int(input("Enter quantity to sell: "))
        
        self.inventory.sell_product(product_id, quantity)
        print("Sale completed successfully!")
    
    def _search_view_menu(self):
        print("\nSearch/View Options:")
        print("1. Search by Name")
        print("2. View All Products")
        print("3. View Electronics")
        print("4. View Groceries")
        print("5. View Clothing")
        print("6. View Inventory Value")
        print("7. Back to Main Menu")
        
        choice = input("Enter your choice (1-7): ")
        if choice == '7':
            return
        
        if choice == '1':
            name = input("Enter name to search: ")
            products = self.inventory.search_by_name(name)
        elif choice == '2':
            products = self.inventory.list_all_products()
        elif choice == '3':
            products = self.inventory.search_by_type(Electronics)
        elif choice == '4':
            products = self.inventory.search_by_type(Grocery)
        elif choice == '5':
            products = self.inventory.search_by_type(Clothing)
        elif choice == '6':
            value = self.inventory.total_inventory_value()
            print(f"\nTotal Inventory Value: ${value:.2f}")
            return
        else:
            print("Invalid choice")
            return
        
        if not products:
            print("No products found")
        else:
            print("\nProducts:")
            for product in products:
                print(f"- {product}")
    
    def _save_inventory_menu(self):
        filename = input("Enter filename to save inventory: ")
        self.inventory.save_to_file(filename)
        print("Inventory saved successfully!")
    
    def _load_inventory_menu(self):
        filename = input("Enter filename to load inventory: ")
        self.inventory.load_from_file(filename)
        print("Inventory loaded successfully!")

# Main execution
if __name__ == "__main__":
    cli = InventoryCLI()
    cli.run()