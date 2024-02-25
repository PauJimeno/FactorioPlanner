import customtkinter as ctk
from PIL import Image

from model.FactorioSolver import FactorioSolver

class InputInterface:
    def __init__(self):
        self.set_theme()
        self.main_window = ctk.CTk()
        self.main_window.geometry("800x600")
        self.main_window.title("FactorioPlanner")
        self.main_window.iconbitmap("sprites/factorio.ico")

        self.set_input_layout()

        self.main_window.mainloop()

    def set_input_layout(self):
        # Create a frame for the input boxes
        input_frame = ctk.CTkFrame(master=self.main_window)
        input_frame.place(relx=0.15, rely=0.15, anchor=ctk.CENTER)

        # Title for the frame
        frame_title = ctk.CTkLabel(master=input_frame, text="MODEL INPUT")
        frame_title.grid(row=0, column=0, columnspan=2)

        # Labels for blueprint size
        width_label = ctk.CTkLabel(master=input_frame, text="Width")
        width_label.grid(row=1, column=0, pady=(0, 5), padx=(10, 5))

        height_label = ctk.CTkLabel(master=input_frame, text="Height")
        height_label.grid(row=2, column=0, pady=(0, 5), padx=(10, 5))

        input_coord_label = ctk.CTkLabel(master=input_frame, text="Input cell")
        input_coord_label.grid(row=3, column=0, pady=(0, 5), padx=(10, 5))

        output_coord_label = ctk.CTkLabel(master=input_frame, text="Output cell")
        output_coord_label.grid(row=4, column=0, pady=(0, 5), padx=(10, 5))

        # Input boxes for blueprint size
        self.blueprint_width_box = ctk.CTkEntry(master=input_frame)
        self.blueprint_width_box.grid(row=1, column=1, padx=(5, 10))

        self.blueprint_height_box = ctk.CTkEntry(master=input_frame)
        self.blueprint_height_box.grid(row=2, column=1, pady=(0, 5), padx=(5, 10))

        self.input_coord_box = ctk.CTkEntry(master=input_frame)
        self.input_coord_box.grid(row=3, column=1, padx=(5, 10))

        self.output_coord_box = ctk.CTkEntry(master=input_frame)
        self.output_coord_box.grid(row=4, column=1, pady=(0, 5), padx=(5, 10))

        # Output image
        pil_image = Image.open('model_image/empty_model.png')
        max_size = (400, 400)
        pil_image.thumbnail(max_size, Image.LANCZOS)
        image = ctk.CTkImage(pil_image, size=(pil_image.width, pil_image.height))
        self.image_label = ctk.CTkLabel(master=self.main_window, image=image, text="Solved Instance",
                                        compound=ctk.BOTTOM)
        self.image_label.place(relx=0.7, rely=0.5, anchor=ctk.CENTER)  # Adjust the position as needed

        # Start solving button
        button = ctk.CTkButton(master=self.main_window, text="Solve Instance", command=self.fetch_entry_data)
        button.place(relx=0.5, rely=0.9, anchor=ctk.CENTER)

        # Label for error messages
        self.error_label = ctk.CTkLabel(master=self.main_window, text="")
        self.error_label.place(relx=0.5, rely=0.05, anchor=ctk.CENTER)

    def set_theme(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

    def fetch_entry_data(self):
        try:
            width = int(self.blueprint_width_box.get())
            height = int(self.blueprint_height_box.get())
            i_x, i_y = map(int, self.input_coord_box.get().split(','))
            o_x, o_y = map(int, self.output_coord_box.get().split(','))
            route_pos = [((i_x, i_y), (o_x, o_y))]

            if 0 <= i_x < height and 0 <= i_y < width and 0 <= o_x < height and 0 <= o_y < width:
                self.error_label.configure(text="Solving ...")
                self.find_model(width, height, route_pos)
            else:
                self.error_label.configure(text="Invalid input. Input/Output coordinates out of the blueprint.")

        except ValueError:
            self.error_label.configure(text="Invalid input. Please enter integers.")

    def find_model(self, blueprint_width, blueprint_height, route_pos):
        # SOLVER DECLARATION #
        solver = FactorioSolver(blueprint_width, blueprint_height, route_pos)

        # FIND A SOLUTION #
        if solver.find_solution():
            self.error_label.configure(text="Model found (SAT)")
            # PRINT THE MODEL OF THE SOLUTION #
            solver.model_to_string()
            solver.model_to_image()
            self.update_model_image()
        else:
            self.error_label.configure(text="No model was found (UNSAT)")

    def update_model_image(self):
        pil_image = Image.open('model_image/game_map_model.png')
        max_size = (400, 400)
        pil_image.thumbnail(max_size, Image.LANCZOS)
        image = ctk.CTkImage(pil_image, size=(pil_image.width, pil_image.height))
        self.image_label.configure(image=image)

