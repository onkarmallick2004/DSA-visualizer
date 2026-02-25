import streamlit as st
import random
import time

st.set_page_config(page_title="Sorting Visualizer UI", layout="wide", page_icon="⚙️")

# We will inject TailwindCSS and custom font (Inter)
st.markdown("""
<script src="https://cdn.tailwindcss.com"></script>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap" rel="stylesheet">
<style>
    :root {
        --bg-color: #0b0f19;
        --sidebar-bg: #111827;
        --accent: #3b82f6;
        --text-main: #f3f4f6;
        --text-muted: #9ca3af;
    }
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif !important;
    }

    /* Streamlit App background */
    .stApp, [data-testid="stAppViewContainer"] {
        background-color: var(--bg-color) !important;
        color: var(--text-main) !important;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: var(--sidebar-bg) !important;
        border-right: 1px solid #1f2937 !important;
    }
    [data-testid="stSidebar"] * {
        color: var(--text-main) !important;
    }
    
    /* Hide top header and footer */
    header[data-testid="stHeader"] {
        background: transparent !important;
    }
    footer, #MainMenu {
        visibility: hidden;
    }

    /* Customize buttons */
    .stButton>button {
        background: linear-gradient(135deg, #2563eb, #1d4ed8) !important;
        color: white !important;
        border: 1px solid #3b82f6 !important;
        border-radius: 10px !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
        box-shadow: 0 4px 14px 0 rgba(37, 99, 235, 0.39) !important;
        transition: transform 0.2s, box-shadow 0.2s !important;
        width: 100% !important;
    }
    .stButton>button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(37, 99, 235, 0.5) !important;
    }
    .stButton>button:active {
        transform: translateY(0) !important;
    }

    /* Adjust main padding */
    .block-container {
        padding-top: 2rem !important;
        max-width: 1200px !important;
    }
</style>
""", unsafe_allow_html=True)


def get_color_theme():
    return {
        "unsorted": {"bg": "#0ea5e9", "glow": "rgba(14, 165, 233, 0.5)", "border": "#0284c7"}, # Cyan
        "comparing": {"bg": "#ec4899", "glow": "rgba(236, 72, 153, 0.6)", "border": "#db2777"}, # Pink
        "pivot": {"bg": "#eab308", "glow": "rgba(234, 179, 8, 0.6)", "border": "#ca8a04"},      # Yellow
        "sorted": {"bg": "#10b981", "glow": "rgba(16, 185, 129, 0.5)", "border": "#059669"},   # Emerald
    }

def color_bars(arr, highlights, pivots, sorted_indices):
    max_val = max(arr) if arr else 1
    theme = get_color_theme()
    
    # Calculate font size based on number of items so numbers always fit
    n = len(arr)
    font_size = "14px"
    if n > 20: font_size = "12px"
    if n > 35: font_size = "10px"
    if n > 50: font_size = "8px"

    bars_html = """<div style="background: #111827; border: 1px solid #1f2937; border-radius: 16px; padding: 24px; box-shadow: 0 10px 25px rgba(0,0,0,0.5);">
<div style="display: flex; align-items: flex-end; justify-content: center; height: 500px; gap: 4px; box-sizing: border-box;">"""
    
    for i, val in enumerate(arr):
        state = "unsorted"
        if i in sorted_indices: state = "sorted"
        elif i in highlights: state = "comparing"
        elif i in pivots: state = "pivot"

        colors = theme[state]
        height_pct = max(5, int((val / max_val) * 100))
        
        # Draw each bar with neon glow, rounded top, and the number sitting inside at the top
        bars_html += f"""
<div style="flex: 1; height: {height_pct}%; background: linear-gradient(180deg, {colors['bg']} 0%, {colors['border']} 100%); border-radius: 8px 8px 0 0; box-shadow: 0 -4px 15px {colors['glow']}, inset 0 2px 4px rgba(255,255,255,0.3); display: flex; flex-direction: column; justify-content: flex-start; align-items: center; transition: height 0.15s ease, background 0.15s ease, box-shadow 0.15s ease; overflow: hidden;">
<span style="color: white; font-weight: 800; font-size: {font_size}; margin-top: 6px; text-shadow: 1px 1px 2px rgba(0,0,0,0.8);">{val}</span>
</div>"""

    bars_html += """
</div>
</div>"""
    return bars_html.replace('\n', '')

def render_legend():
    theme = get_color_theme()
    legend_html = f"""<div style="display: flex; justify-content: center; gap: 30px; margin-top: 20px; padding: 15px; background: #111827; border-radius: 12px; border: 1px solid #1f2937;">
    <div style="display: flex; align-items: center; gap: 10px;">
        <div style="width: 16px; height: 16px; border-radius: 4px; background: {theme['unsorted']['bg']}; box-shadow: 0 0 10px {theme['unsorted']['glow']};"></div>
        <span style="color: #d1d5db; font-weight: 600; font-size: 14px;">Unsorted</span>
    </div>
    <div style="display: flex; align-items: center; gap: 10px;">
        <div style="width: 16px; height: 16px; border-radius: 4px; background: {theme['comparing']['bg']}; box-shadow: 0 0 10px {theme['comparing']['glow']};"></div>
        <span style="color: #d1d5db; font-weight: 600; font-size: 14px;">Comparing</span>
    </div>
    <div style="display: flex; align-items: center; gap: 10px;">
        <div style="width: 16px; height: 16px; border-radius: 4px; background: {theme['pivot']['bg']}; box-shadow: 0 0 10px {theme['pivot']['glow']};"></div>
        <span style="color: #d1d5db; font-weight: 600; font-size: 14px;">Pivot</span>
    </div>
    <div style="display: flex; align-items: center; gap: 10px;">
        <div style="width: 16px; height: 16px; border-radius: 4px; background: {theme['sorted']['bg']}; box-shadow: 0 0 10px {theme['sorted']['glow']};"></div>
        <span style="color: #d1d5db; font-weight: 600; font-size: 14px;">Sorted</span>
    </div>
</div>"""
    return legend_html.replace('\n', '')

# --- ALGORITHM GENERATORS ---
def bubble_sort(arr):
    n = len(arr)
    sorted_idx = []
    yield arr, [], [], sorted_idx
    for i in range(n):
        for j in range(0, n - i - 1):
            yield arr, [j, j+1], [], sorted_idx
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                yield arr, [j, j+1], [], sorted_idx
        sorted_idx.append(n - i - 1)
        if n-i-1 == 0: sorted_idx.append(0)
    sorted_idx = list(range(n))
    yield arr, [], [], sorted_idx

def insertion_sort(arr):
    n = len(arr)
    sorted_idx = [0]
    yield arr, [], [], sorted_idx
    for i in range(1, n):
        key = arr[i]
        j = i - 1
        while j >= 0 and key < arr[j]:
            yield arr, [j, j+1], [], sorted_idx
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key
        sorted_idx.append(i)
        yield arr, [j+1], [], sorted_idx
    sorted_idx = list(range(n))
    yield arr, [], [], sorted_idx

def selection_sort(arr):
    n = len(arr)
    sorted_idx = []
    yield arr, [], [], sorted_idx
    for i in range(n):
        min_idx = i
        for j in range(i + 1, n):
            yield arr, [min_idx, j], [], sorted_idx
            if arr[j] < arr[min_idx]:
                min_idx = j
        arr[i], arr[min_idx] = arr[min_idx], arr[i]
        sorted_idx.append(i)
        yield arr, [], [], sorted_idx
    sorted_idx = list(range(n))
    yield arr, [], [], sorted_idx

def merge_sort(arr):
    n = len(arr)
    sorted_idx = []
    def merge_sort_helper(arr, l, r):
        if l < r:
            m = l + (r - l) // 2
            yield from merge_sort_helper(arr, l, m)
            yield from merge_sort_helper(arr, m + 1, r)
            yield from merge(arr, l, m, r)
    def merge(arr, l, m, r):
        L = arr[l:m+1]
        R = arr[m+1:r+1]
        i = 0; j = 0; k = l
        while i < len(L) and j < len(R):
            yield arr, [k], [], []
            if L[i] <= R[j]: arr[k] = L[i]; i += 1
            else: arr[k] = R[j]; j += 1
            k += 1
        while i < len(L):
            arr[k] = L[i]; i += 1; k += 1
            yield arr, [k-1], [], []
        while j < len(R):
            arr[k] = R[j]; j += 1; k += 1
            yield arr, [k-1], [], []
        yield arr, list(range(l, r+1)), [], []
    yield arr, [], [], sorted_idx
    yield from merge_sort_helper(arr, 0, n - 1)
    sorted_idx = list(range(n))
    yield arr, [], [], sorted_idx

def quick_sort(arr):
    n = len(arr)
    sorted_idx = []
    def quick_sort_helper(arr, low, high):
        if low < high:
            pi, _ = yield from partition(arr, low, high)
            sorted_idx.append(pi)
            yield from quick_sort_helper(arr, low, pi - 1)
            yield from quick_sort_helper(arr, pi + 1, high)
        elif low == high:
            sorted_idx.append(low)
            yield arr, [], [], sorted_idx
    def partition(arr, low, high):
        pivot = arr[high]
        i = low - 1
        for j in range(low, high):
            yield arr, [j], [high], sorted_idx
            if arr[j] < pivot:
                i += 1
                arr[i], arr[j] = arr[j], arr[i]
                yield arr, [i, j], [high], sorted_idx
        arr[i + 1], arr[high] = arr[high], arr[i + 1]
        yield arr, [i+1, high], [high], sorted_idx
        return i + 1, []
    yield arr, [], [], sorted_idx
    yield from quick_sort_helper(arr, 0, n - 1)
    sorted_idx = list(range(n))
    yield arr, [], [], sorted_idx


# --- MAIN UI COMPONENT ---
def main():
    st.markdown("""
<div style="text-align: center; margin-bottom: 2rem;">
    <h1 style="color: #f3f4f6; font-size: 3rem; font-weight: 800; margin: 0; text-shadow: 0 0 20px rgba(59, 130, 246, 0.5);">
        Algorithm Visualizer
    </h1>
    <p style="color: #9ca3af; font-size: 1.1rem; margin-top: 0.5rem;">
        High-performance sorting engine visualization
    </p>
</div>
""", unsafe_allow_html=True)

    with st.sidebar:
        st.markdown("""
<h2 style="color: #f3f4f6; font-size: 1.5rem; font-weight: 800; margin-bottom: 2rem; border-bottom: 2px solid #1f2937; padding-bottom: 0.5rem;">
    Control Panel
</h2>
""", unsafe_allow_html=True)
        
        st.markdown("<p style='color: #9ca3af; font-weight: 600; margin-bottom: 0.25rem;'>ALGORITHM</p>", unsafe_allow_html=True)
        algorithm = st.selectbox("Algorithm", 
            ("Bubble Sort", "Insertion Sort", "Selection Sort", "Merge Sort", "Quick Sort"), 
            label_visibility="collapsed"
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<p style='color: #9ca3af; font-weight: 600; margin-bottom: 0.25rem;'>ARRAY DENSITY</p>", unsafe_allow_html=True)
        array_size = st.slider("Array Density", min_value=10, max_value=60, value=30, label_visibility="collapsed")
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<p style='color: #9ca3af; font-weight: 600; margin-bottom: 0.25rem;'>EXECUTION SPEED</p>", unsafe_allow_html=True)
        speed = st.slider("Execution Speed", min_value=0.1, max_value=2.0, value=1.5, step=0.1, label_visibility="collapsed")
        delay = max(0.01, 2.05 - speed)

        st.markdown("<br><br>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            regen = st.button("Shuffle Array")
        with col2:
            run = st.button("Run Sort")

    # Session State
    if 'arr' not in st.session_state or len(st.session_state.arr) != array_size:
        st.session_state.arr = [random.randint(5, 100) for _ in range(array_size)]
        st.session_state.sorting = False
    if 'sorting' not in st.session_state:
        st.session_state.sorting = False

    if regen:
        st.session_state.arr = [random.randint(5, 100) for _ in range(array_size)]
        st.session_state.sorting = False
    if run:
        st.session_state.sorting = True

    # Main Canvas Placeholders
    canvas_ph = st.empty()
    legend_ph = st.empty()

    if not st.session_state.sorting:
        canvas_ph.markdown(color_bars(st.session_state.arr, [], [], []), unsafe_allow_html=True)
        legend_ph.markdown(render_legend(), unsafe_allow_html=True)

    if st.session_state.sorting:
        arr_copy = st.session_state.arr.copy()

        gens = {
            "Bubble Sort": bubble_sort,
            "Insertion Sort": insertion_sort,
            "Selection Sort": selection_sort,
            "Merge Sort": merge_sort,
            "Quick Sort": quick_sort,
        }
        generator = gens[algorithm](arr_copy)

        for frame in generator:
            current_arr, highlights, pivots, sorted_indices = frame
            canvas_ph.markdown(color_bars(current_arr, highlights, pivots, sorted_indices), unsafe_allow_html=True)
            legend_ph.markdown(render_legend(), unsafe_allow_html=True)
            time.sleep(delay)

        st.session_state.sorting = False
        st.session_state.arr = arr_copy


if __name__ == "__main__":
    main()
