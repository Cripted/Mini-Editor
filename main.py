"""
Mini-Editor Gráfico Interactivo
Autor: Sistema de Desarrollo
Versión: 1.1
Descripción: Editor gráfico con transformaciones geométricas y vista previa en tiempo real
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import json
import math
from typing import List, Tuple, Optional, Dict, Any


class Point:
    """Representa un punto en el plano 2D"""
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
    
    def to_dict(self) -> Dict:
        return {"x": self.x, "y": self.y}
    
    @staticmethod
    def from_dict(data: Dict) -> 'Point':
        return Point(data["x"], data["y"])


class GraphicObject:
    """Clase base para todos los objetos gráficos"""
    def __init__(self, obj_type: str, color: str = "black"):
        self.type = obj_type
        self.color = color
        self.canvas_id = None
        self.selected = False
    
    def draw(self, canvas: tk.Canvas) -> int:
        """Dibuja el objeto en el canvas. Debe ser implementado por subclases"""
        raise NotImplementedError
    
    def scale(self, factor: float, center: Point):
        """Aplica transformación de escala"""
        raise NotImplementedError
    
    def translate(self, dx: float, dy: float):
        """Aplica transformación de traslación"""
        raise NotImplementedError
    
    def rotate(self, angle: float, center: Point):
        """Aplica transformación de rotación (ángulo en grados)"""
        raise NotImplementedError
    
    def contains_point(self, x: float, y: float) -> bool:
        """Verifica si un punto está dentro del objeto"""
        raise NotImplementedError
    
    def to_dict(self) -> Dict:
        """Serializa el objeto a diccionario"""
        raise NotImplementedError
    
    @staticmethod
    def from_dict(data: Dict) -> 'GraphicObject':
        """Deserializa desde diccionario"""
        obj_type = data["type"]
        if obj_type == "circle":
            return Circle.from_dict(data)
        elif obj_type == "rectangle":
            return Rectangle.from_dict(data)
        elif obj_type == "line":
            return Line.from_dict(data)
        elif obj_type == "polygon":
            return Polygon.from_dict(data)
        return None


class Circle(GraphicObject):
    """Representa un círculo"""
    def __init__(self, center: Point, radius: float, color: str = "black"):
        super().__init__("circle", color)
        self.center = center
        self.radius = radius
    
    def draw(self, canvas: tk.Canvas) -> int:
        x, y, r = self.center.x, self.center.y, self.radius
        outline = "red" if self.selected else self.color
        width = 3 if self.selected else 1
        self.canvas_id = canvas.create_oval(
            x - r, y - r, x + r, y + r,
            outline=outline, width=width
        )
        return self.canvas_id
    
    def scale(self, factor: float, center: Point):
        self.radius *= factor
        dx = self.center.x - center.x
        dy = self.center.y - center.y
        self.center.x = center.x + dx * factor
        self.center.y = center.y + dy * factor
    
    def translate(self, dx: float, dy: float):
        self.center.x += dx
        self.center.y += dy
    
    def rotate(self, angle: float, center: Point):
        rad = math.radians(angle)
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)
        
        dx = self.center.x - center.x
        dy = self.center.y - center.y
        
        new_x = dx * cos_a - dy * sin_a
        new_y = dx * sin_a + dy * cos_a
        
        self.center.x = center.x + new_x
        self.center.y = center.y + new_y
    
    def contains_point(self, x: float, y: float) -> bool:
        dist = math.sqrt((x - self.center.x)**2 + (y - self.center.y)**2)
        return dist <= self.radius
    
    def to_dict(self) -> Dict:
        return {
            "type": "circle",
            "center": self.center.to_dict(),
            "radius": self.radius,
            "color": self.color
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'Circle':
        return Circle(
            Point.from_dict(data["center"]),
            data["radius"],
            data["color"]
        )


class Rectangle(GraphicObject):
    """Representa un rectángulo"""
    def __init__(self, p1: Point, p2: Point, color: str = "black"):
        super().__init__("rectangle", color)
        self.p1 = p1
        self.p2 = p2
    
    def draw(self, canvas: tk.Canvas) -> int:
        outline = "red" if self.selected else self.color
        width = 3 if self.selected else 1
        self.canvas_id = canvas.create_rectangle(
            self.p1.x, self.p1.y, self.p2.x, self.p2.y,
            outline=outline, width=width
        )
        return self.canvas_id
    
    def get_center(self) -> Point:
        return Point((self.p1.x + self.p2.x) / 2, (self.p1.y + self.p2.y) / 2)
    
    def scale(self, factor: float, center: Point):
        self.p1.x = center.x + (self.p1.x - center.x) * factor
        self.p1.y = center.y + (self.p1.y - center.y) * factor
        self.p2.x = center.x + (self.p2.x - center.x) * factor
        self.p2.y = center.y + (self.p2.y - center.y) * factor
    
    def translate(self, dx: float, dy: float):
        self.p1.x += dx
        self.p1.y += dy
        self.p2.x += dx
        self.p2.y += dy
    
    def rotate(self, angle: float, center: Point):
        rad = math.radians(angle)
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)
        
        dx1 = self.p1.x - center.x
        dy1 = self.p1.y - center.y
        self.p1.x = center.x + dx1 * cos_a - dy1 * sin_a
        self.p1.y = center.y + dx1 * sin_a + dy1 * cos_a
        
        dx2 = self.p2.x - center.x
        dy2 = self.p2.y - center.y
        self.p2.x = center.x + dx2 * cos_a - dy2 * sin_a
        self.p2.y = center.y + dx2 * sin_a + dy2 * cos_a
    
    def contains_point(self, x: float, y: float) -> bool:
        min_x = min(self.p1.x, self.p2.x)
        max_x = max(self.p1.x, self.p2.x)
        min_y = min(self.p1.y, self.p2.y)
        max_y = max(self.p1.y, self.p2.y)
        return min_x <= x <= max_x and min_y <= y <= max_y
    
    def to_dict(self) -> Dict:
        return {
            "type": "rectangle",
            "p1": self.p1.to_dict(),
            "p2": self.p2.to_dict(),
            "color": self.color
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'Rectangle':
        return Rectangle(
            Point.from_dict(data["p1"]),
            Point.from_dict(data["p2"]),
            data["color"]
        )


class Line(GraphicObject):
    """Representa una línea"""
    def __init__(self, p1: Point, p2: Point, color: str = "black"):
        super().__init__("line", color)
        self.p1 = p1
        self.p2 = p2
    
    def draw(self, canvas: tk.Canvas) -> int:
        outline = "red" if self.selected else self.color
        width = 3 if self.selected else 1
        self.canvas_id = canvas.create_line(
            self.p1.x, self.p1.y, self.p2.x, self.p2.y,
            fill=outline, width=width
        )
        return self.canvas_id
    
    def scale(self, factor: float, center: Point):
        self.p1.x = center.x + (self.p1.x - center.x) * factor
        self.p1.y = center.y + (self.p1.y - center.y) * factor
        self.p2.x = center.x + (self.p2.x - center.x) * factor
        self.p2.y = center.y + (self.p2.y - center.y) * factor
    
    def translate(self, dx: float, dy: float):
        self.p1.x += dx
        self.p1.y += dy
        self.p2.x += dx
        self.p2.y += dy
    
    def rotate(self, angle: float, center: Point):
        rad = math.radians(angle)
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)
        
        dx1 = self.p1.x - center.x
        dy1 = self.p1.y - center.y
        self.p1.x = center.x + dx1 * cos_a - dy1 * sin_a
        self.p1.y = center.y + dx1 * sin_a + dy1 * cos_a
        
        dx2 = self.p2.x - center.x
        dy2 = self.p2.y - center.y
        self.p2.x = center.x + dx2 * cos_a - dy2 * sin_a
        self.p2.y = center.y + dx2 * sin_a + dy2 * cos_a
    
    def contains_point(self, x: float, y: float) -> bool:
        dx = self.p2.x - self.p1.x
        dy = self.p2.y - self.p1.y
        length = math.sqrt(dx**2 + dy**2)
        if length == 0:
            return False
        
        dist = abs(dy * x - dx * y + self.p2.x * self.p1.y - self.p2.y * self.p1.x) / length
        return dist < 5
    
    def to_dict(self) -> Dict:
        return {
            "type": "line",
            "p1": self.p1.to_dict(),
            "p2": self.p2.to_dict(),
            "color": self.color
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'Line':
        return Line(
            Point.from_dict(data["p1"]),
            Point.from_dict(data["p2"]),
            data["color"]
        )


class Polygon(GraphicObject):
    """Representa un polígono"""
    def __init__(self, points: List[Point], color: str = "black"):
        super().__init__("polygon", color)
        self.points = points
    
    def draw(self, canvas: tk.Canvas) -> int:
        coords = []
        for p in self.points:
            coords.extend([p.x, p.y])
        
        outline = "red" if self.selected else self.color
        width = 3 if self.selected else 1
        self.canvas_id = canvas.create_polygon(
            *coords, outline=outline, fill="", width=width
        )
        return self.canvas_id
    
    def get_center(self) -> Point:
        cx = sum(p.x for p in self.points) / len(self.points)
        cy = sum(p.y for p in self.points) / len(self.points)
        return Point(cx, cy)
    
    def scale(self, factor: float, center: Point):
        for p in self.points:
            p.x = center.x + (p.x - center.x) * factor
            p.y = center.y + (p.y - center.y) * factor
    
    def translate(self, dx: float, dy: float):
        for p in self.points:
            p.x += dx
            p.y += dy
    
    def rotate(self, angle: float, center: Point):
        rad = math.radians(angle)
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)
        
        for p in self.points:
            dx = p.x - center.x
            dy = p.y - center.y
            p.x = center.x + dx * cos_a - dy * sin_a
            p.y = center.y + dx * sin_a + dy * cos_a
    
    def contains_point(self, x: float, y: float) -> bool:
        n = len(self.points)
        inside = False
        
        j = n - 1
        for i in range(n):
            xi, yi = self.points[i].x, self.points[i].y
            xj, yj = self.points[j].x, self.points[j].y
            
            if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi) + xi):
                inside = not inside
            j = i
        
        return inside
    
    def to_dict(self) -> Dict:
        return {
            "type": "polygon",
            "points": [p.to_dict() for p in self.points],
            "color": self.color
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'Polygon':
        return Polygon(
            [Point.from_dict(p) for p in data["points"]],
            data["color"]
        )


class GraphicEditor:
    """Editor gráfico principal"""
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Mini-Editor Gráfico Interactivo v1.1")
        self.root.geometry("1000x700")
        
        self.objects: List[GraphicObject] = []
        self.selected_object: Optional[GraphicObject] = None
        self.current_tool = "select"
        self.temp_points: List[Point] = []
        self.drag_start: Optional[Point] = None
        
        # IDs para vista previa temporal
        self.preview_ids = []
        self.dimension_text_id = None
        
        self.setup_ui()
    
    def setup_ui(self):
        """Configura la interfaz de usuario"""
        toolbar = tk.Frame(self.root, bg="lightgray", height=60)
        toolbar.pack(side=tk.TOP, fill=tk.X)
        
        tools = [
            ("Seleccionar", "select"),
            ("Círculo", "circle"),
            ("Rectángulo", "rectangle"),
            ("Línea", "line"),
            ("Polígono", "polygon")
        ]
        
        for text, tool in tools:
            btn = tk.Button(toolbar, text=text, command=lambda t=tool: self.set_tool(t))
            btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        tk.Frame(toolbar, width=2, bg="gray").pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        tk.Button(toolbar, text="Escalar", command=self.apply_scale).pack(side=tk.LEFT, padx=5)
        tk.Button(toolbar, text="Trasladar", command=self.apply_translate).pack(side=tk.LEFT, padx=5)
        tk.Button(toolbar, text="Rotar", command=self.apply_rotate).pack(side=tk.LEFT, padx=5)
        
        tk.Frame(toolbar, width=2, bg="gray").pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        tk.Button(toolbar, text="Borrar", command=self.delete_object).pack(side=tk.LEFT, padx=5)
        tk.Button(toolbar, text="Guardar", command=self.save_project).pack(side=tk.LEFT, padx=5)
        tk.Button(toolbar, text="Cargar", command=self.load_project).pack(side=tk.LEFT, padx=5)
        
        self.canvas = tk.Canvas(self.root, bg="white", cursor="cross")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        
        self.status_bar = tk.Label(self.root, text="Herramienta: Seleccionar", 
                                   bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def set_tool(self, tool: str):
        """Cambia la herramienta actual"""
        self.current_tool = tool
        self.temp_points = []
        self.clear_preview()
        self.status_bar.config(text=f"Herramienta: {tool.capitalize()}")
        
        if tool == "polygon":
            messagebox.showinfo("Polígono", 
                              "Haga clic para agregar puntos.\nHaga clic derecho para finalizar.")
            self.canvas.bind("<Button-3>", self.finish_polygon)
    
    def clear_preview(self):
        """Limpia todos los elementos de vista previa"""
        for pid in self.preview_ids:
            self.canvas.delete(pid)
        self.preview_ids = []
        if self.dimension_text_id:
            self.canvas.delete(self.dimension_text_id)
            self.dimension_text_id = None
    
    def draw_preview_circle(self, x1: float, y1: float, x2: float, y2: float):
        """Dibuja vista previa de círculo con dimensiones"""
        self.clear_preview()
        
        radius = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        
        # Dibujar círculo de vista previa
        pid = self.canvas.create_oval(
            x1 - radius, y1 - radius, x1 + radius, y1 + radius,
            outline="blue", dash=(4, 4), width=2
        )
        self.preview_ids.append(pid)
        
        # Dibujar línea del radio
        line_id = self.canvas.create_line(
            x1, y1, x2, y2,
            fill="blue", dash=(2, 2)
        )
        self.preview_ids.append(line_id)
        
        # Mostrar dimensiones
        text = f"Radio: {radius:.1f} px\nDiámetro: {radius*2:.1f} px"
        self.dimension_text_id = self.canvas.create_text(
            x2 + 10, y2 - 10,
            text=text, fill="blue", font=("Arial", 10, "bold"),
            anchor="w"
        )
    
    def draw_preview_rectangle(self, x1: float, y1: float, x2: float, y2: float):
        """Dibuja vista previa de rectángulo con dimensiones"""
        self.clear_preview()
        
        width = abs(x2 - x1)
        height = abs(y2 - y1)
        
        # Dibujar rectángulo de vista previa
        pid = self.canvas.create_rectangle(
            x1, y1, x2, y2,
            outline="blue", dash=(4, 4), width=2
        )
        self.preview_ids.append(pid)
        
        # Mostrar dimensiones
        text = f"Ancho: {width:.1f} px\nAlto: {height:.1f} px\nÁrea: {width*height:.1f} px²"
        text_x = (x1 + x2) / 2
        text_y = min(y1, y2) - 20
        
        self.dimension_text_id = self.canvas.create_text(
            text_x, text_y,
            text=text, fill="blue", font=("Arial", 10, "bold"),
            anchor="s"
        )
    
    def draw_preview_line(self, x1: float, y1: float, x2: float, y2: float):
        """Dibuja vista previa de línea con dimensiones"""
        self.clear_preview()
        
        length = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        angle = math.degrees(math.atan2(y2 - y1, x2 - x1))
        
        # Dibujar línea de vista previa
        pid = self.canvas.create_line(
            x1, y1, x2, y2,
            fill="blue", dash=(4, 4), width=2
        )
        self.preview_ids.append(pid)
        
        # Mostrar dimensiones
        text = f"Longitud: {length:.1f} px\nÁngulo: {angle:.1f}°"
        text_x = (x1 + x2) / 2
        text_y = (y1 + y2) / 2 - 15
        
        self.dimension_text_id = self.canvas.create_text(
            text_x, text_y,
            text=text, fill="blue", font=("Arial", 10, "bold"),
            anchor="s"
        )
    
    def on_click(self, event):
        """Maneja el evento de clic"""
        x, y = event.x, event.y
        
        if self.current_tool == "select":
            self.select_object(x, y)
            if self.selected_object:
                self.drag_start = Point(x, y)
        
        elif self.current_tool == "circle":
            self.temp_points = [Point(x, y)]
            self.status_bar.config(text="Arrastre para definir el radio")
        
        elif self.current_tool == "rectangle":
            self.temp_points = [Point(x, y)]
            self.status_bar.config(text="Arrastre para definir el rectángulo")
        
        elif self.current_tool == "line":
            self.temp_points = [Point(x, y)]
            self.status_bar.config(text="Arrastre para definir la línea")
        
        elif self.current_tool == "polygon":
            self.temp_points.append(Point(x, y))
            self.status_bar.config(text=f"Puntos: {len(self.temp_points)} (Clic derecho para finalizar)")
    
    def on_drag(self, event):
        """Maneja el evento de arrastre"""
        x, y = event.x, event.y
        
        if self.current_tool == "select" and self.selected_object and self.drag_start:
            dx = x - self.drag_start.x
            dy = y - self.drag_start.y
            self.selected_object.translate(dx, dy)
            self.drag_start = Point(x, y)
            self.redraw()
        
        elif self.current_tool == "circle" and len(self.temp_points) == 1:
            p = self.temp_points[0]
            self.draw_preview_circle(p.x, p.y, x, y)
        
        elif self.current_tool == "rectangle" and len(self.temp_points) == 1:
            p = self.temp_points[0]
            self.draw_preview_rectangle(p.x, p.y, x, y)
        
        elif self.current_tool == "line" and len(self.temp_points) == 1:
            p = self.temp_points[0]
            self.draw_preview_line(p.x, p.y, x, y)
    
    def on_release(self, event):
        """Maneja el evento de liberación del mouse"""
        x, y = event.x, event.y
        
        if self.current_tool == "circle" and len(self.temp_points) == 1:
            center = self.temp_points[0]
            radius = math.sqrt((x - center.x)**2 + (y - center.y)**2)
            if radius > 5:
                circle = Circle(center, radius)
                self.objects.append(circle)
                self.redraw()
            self.temp_points = []
            self.clear_preview()
        
        elif self.current_tool == "rectangle" and len(self.temp_points) == 1:
            p1 = self.temp_points[0]
            p2 = Point(x, y)
            if abs(x - p1.x) > 5 and abs(y - p1.y) > 5:
                rect = Rectangle(p1, p2)
                self.objects.append(rect)
                self.redraw()
            self.temp_points = []
            self.clear_preview()
        
        elif self.current_tool == "line" and len(self.temp_points) == 1:
            p1 = self.temp_points[0]
            p2 = Point(x, y)
            if math.sqrt((x - p1.x)**2 + (y - p1.y)**2) > 5:
                line = Line(p1, p2)
                self.objects.append(line)
                self.redraw()
            self.temp_points = []
            self.clear_preview()
        
        self.drag_start = None
    
    def finish_polygon(self, event=None):
        """Finaliza la creación de un polígono"""
        if len(self.temp_points) >= 3:
            polygon = Polygon(self.temp_points)
            self.objects.append(polygon)
            self.redraw()
        self.temp_points = []
        self.canvas.unbind("<Button-3>")
    
    def select_object(self, x: float, y: float):
        """Selecciona un objeto en las coordenadas dadas"""
        if self.selected_object:
            self.selected_object.selected = False
        
        self.selected_object = None
        
        for obj in reversed(self.objects):
            if obj.contains_point(x, y):
                obj.selected = True
                self.selected_object = obj
                break
        
        self.redraw()
    
    def delete_object(self):
        """Elimina el objeto seleccionado"""
        if self.selected_object:
            self.objects.remove(self.selected_object)
            self.selected_object = None
            self.redraw()
        else:
            messagebox.showwarning("Advertencia", "No hay ningún objeto seleccionado")
    
    def apply_scale(self):
        """Aplica transformación de escala"""
        if not self.selected_object:
            messagebox.showwarning("Advertencia", "Seleccione un objeto primero")
            return
        
        factor = simpledialog.askfloat("Escalar", 
                                       "Ingrese el factor de escala (ej: 1.5 para aumentar 50%):",
                                       minvalue=0.1, maxvalue=10.0)
        if factor:
            if hasattr(self.selected_object, 'center'):
                center = self.selected_object.center
            elif hasattr(self.selected_object, 'get_center'):
                center = self.selected_object.get_center()
            else:
                center = Point(400, 300)
            
            self.selected_object.scale(factor, center)
            self.redraw()
    
    def apply_translate(self):
        """Aplica transformación de traslación"""
        if not self.selected_object:
            messagebox.showwarning("Advertencia", "Seleccione un objeto primero")
            return
        
        dx = simpledialog.askfloat("Trasladar", "Ingrese el desplazamiento en X:")
        if dx is None:
            return
        
        dy = simpledialog.askfloat("Trasladar", "Ingrese el desplazamiento en Y:")
        if dy is None:
            return
        
        self.selected_object.translate(dx, dy)
        self.redraw()
    
    def apply_rotate(self):
        """Aplica transformación de rotación"""
        if not self.selected_object:
            messagebox.showwarning("Advertencia", "Seleccione un objeto primero")
            return
        
        angle = simpledialog.askfloat("Rotar", 
                                     "Ingrese el ángulo de rotación en grados:",
                                     minvalue=-360, maxvalue=360)
        if angle is not None:
            if hasattr(self.selected_object, 'center'):
                center = self.selected_object.center
            elif hasattr(self.selected_object, 'get_center'):
                center = self.selected_object.get_center()
            else:
                center = Point(400, 300)
            
            self.selected_object.rotate(angle, center)
            self.redraw()
    
    def save_project(self):
        """Guarda el proyecto en un archivo JSON"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                data = {
                    "version": "1.0",
                    "objects": [obj.to_dict() for obj in self.objects]
                }
                
                with open(filename, 'w') as f:
                    json.dump(data, f, indent=2)
                
                messagebox.showinfo("Éxito", "Proyecto guardado correctamente")
            except Exception as e:
                messagebox.showerror("Error", f"Error al guardar: {str(e)}")
    
    def load_project(self):
        """Carga un proyecto desde un archivo JSON"""
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'r') as f:
                    data = json.load(f)
                
                self.objects = []
                for obj_data in data["objects"]:
                    obj = GraphicObject.from_dict(obj_data)
                    if obj:
                        self.objects.append(obj)
                
                self.selected_object = None
                self.clear_preview()
                self.redraw()
                messagebox.showinfo("Éxito", "Proyecto cargado correctamente")
            except Exception as e:
                messagebox.showerror("Error", f"Error al cargar: {str(e)}")
    
    def redraw(self):
        """Redibuja todos los objetos en el canvas"""
        self.canvas.delete("all")
        for obj in self.objects:
            obj.draw(self.canvas)


def main():
    """Función principal"""
    root = tk.Tk()
    app = GraphicEditor(root)
    root.mainloop()


if __name__ == "__main__":
    main()