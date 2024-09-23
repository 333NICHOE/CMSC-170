import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import re
from collections import Counter

class BagOfWordsApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Bag-of-Words")
        self.root.geometry("500x500")
        self.root.configure(bg='#e1eff6')
        self.create_widgets()

    def create_widgets(self):
        header_frame = tk.Frame(self.root, bg='#1c74bb', bd=2, relief=tk.GROOVE)
        header_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        title_label = tk.Label(header_frame, text="Bag-of-Words", font=('Helvetica', 24, 'bold'), fg='white', bg='#1c74bb')
        title_label.pack()

        course_label = tk.Label(header_frame, text="CMSC 170", font=('Helvetica', 14), fg='white', bg='#1c74bb')
        course_label.pack()

        author_label = tk.Label(header_frame, text="Nico Antonio L. Montero", font=('Helvetica', 14), fg='white', bg='#1c74bb')
        author_label.pack()

        self.selectFolder = tk.Button(self.root, text="Select Folder", command=self.textConversion, bg='#4b9cd3', fg='white', font=('Helvetica', 12, 'bold'), bd=0, padx=20, pady=10)
        self.selectFolder.pack(side=tk.TOP, pady=10)

        info_frame = tk.Frame(self.root, bg='#e1eff6')
        info_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        self.dictSize = tk.Label(info_frame, text="Dictionary Size: ", font=('Helvetica', 12), bg='#e1eff6')
        self.dictSize.pack(side=tk.LEFT)

        self.wordCount = tk.Label(info_frame, text="Total Word Count: ", font=('Helvetica', 12), bg='#e1eff6')
        self.wordCount.pack(side=tk.LEFT, padx=20)

        table_frame = tk.Frame(self.root, bg='#e1eff6', bd=2, relief=tk.SOLID)
        table_frame.pack(side=tk.TOP, fill=tk.BOTH, padx=10, pady=10, expand=True)

        self.scrollbar_y = tk.Scrollbar(table_frame, orient=tk.VERTICAL)
        self.wordFrequency = ttk.Treeview(table_frame, columns=("Word", "Frequency"), show="headings", yscrollcommand=self.scrollbar_y.set)
        self.scrollbar_y.config(command=self.wordFrequency.yview)
        self.scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)

        self.wordFrequency.heading("Word", text="Word")
        self.wordFrequency.heading("Frequency", text="Frequency")
        self.wordFrequency.column("Word", width=300, anchor='center')
        self.wordFrequency.column("Frequency", width=150, anchor='center')
        self.wordFrequency.pack(fill=tk.BOTH, expand=True)

    def textConversion(self):
        # Initialize a Counter to keep track of word frequencies
        word_count = Counter()
        total_words = 0

        # Open a dialog to select a folder
        folder = filedialog.askdirectory()
        if not folder:
            return

        # Iterate over each file in the selected folder
        for file in os.listdir(folder):
            path = os.path.join(folder, file)
            try:
                # Open and read the file
                with open(path, 'r', encoding='latin-1') as f:
                    for line in f:
                        # Convert text to lowercase and remove non-alphabetic characters
                        text = line.lower()
                        text = re.sub(r'[^a-z\s]', '', text)
                        words = text.split()
                        # Update the word count
                        word_count.update(words)
                        total_words += len(words)
            except Exception as e:
                # Show an error message if file processing fails
                messagebox.showerror("Error", f"Failed to process {file}: {e}")

            # Keep UI responsive during processing
            self.root.update_idletasks()

        # Update the dictionary size and total word count labels
        dict_size = len(word_count)
        self.dictSize.config(text=f"Dictionary Size: {dict_size}")
        self.wordCount.config(text=f"Total Word Count: {total_words}")

        # Sort the word count dictionary
        sorted_word_count = sorted(word_count.items())
        # Save the results to a file
        self.saveToFile(sorted_word_count, dict_size, total_words)
        # Load the results into the table
        self.loadTable(sorted_word_count)

    def saveToFile(self, word_freq_list, dict_size, total_words):
        # Save the word frequencies to a file
        with open("bow.out", "w") as output:
            output.write(f"Dictionary Size: \t {dict_size}\n")
            output.write(f"Total Word Count: \t {total_words}\n\n")
            for word, freq in word_freq_list:
                output.write(f"{word} {freq}\n")

    def loadTable(self, word_freq_list):
        # Clear the existing rows in the table
        for row in self.wordFrequency.get_children():
            self.wordFrequency.delete(row)

        # Inserting new pairs
        for word, freq in word_freq_list:
            self.wordFrequency.insert('', 'end', values=(word, freq))

        # Update the UI
        self.root.update_idletasks()


root = tk.Tk()
app = BagOfWordsApp(root)
root.mainloop()
