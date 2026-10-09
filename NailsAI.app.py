import io, math, random
import numpy as np
import streamlit as st
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
from streamlit_drawable_canvas import st_canvas

st.set_page_config(page_title="AI Nail Stylist", page_icon="💅", layout="wide")

# Большой встроенный каталог дизайнов. Новые варианты можно добавлять в этот список.
DESIGNS = [
    ("Классический нюд", "Классика", "#D9A39A", "#F6DCD4", "plain"),
    ("Молочный", "Классика", "#F6EEE7", "#FFFFFF", "plain"),
    ("Красный глянец", "Классика", "#C8102E", "#FF5364", "plain"),
    ("Чёрный глянец", "Классика", "#17151A", "#57515B", "plain"),
    ("Бордовый люкс", "Люкс", "#64152D", "#C04A63", "chrome"),
    ("Розовый жемчуг", "Люкс", "#E9BFCB", "#FFF0F5", "pearl"),
    ("Золотой хром", "Люкс", "#B7832F", "#FFE7A0", "chrome"),
    ("Серебряный хром", "Люкс", "#8D929B", "#F8FAFF", "chrome"),
    ("Глаз кошки: изумруд", "Люкс", "#064E46", "#42D6B3", "cat_eye"),
    ("Глаз кошки: аметист", "Люкс", "#44205F", "#C59AFF", "cat_eye"),
    ("Френч белый", "Френч", "#F4E8DF", "#FFFFFF", "french"),
    ("Френч красный", "Френч", "#F1D8D2", "#D7193F", "french"),
    ("Френч чёрный", "Френч", "#EEDDD5", "#17151A", "french"),
    ("Френч цветной", "Френч", "#F5E4DC", "#A45DE4", "french"),
    ("Baby boomer", "Градиент", "#E7B9B8", "#FFF8F5", "ombre"),
    ("Розовый градиент", "Градиент", "#E85D91", "#FFD7E6", "ombre"),
    ("Закат", "Градиент", "#F05B48", "#FFC65C", "ombre"),
    ("Океан", "Градиент", "#075985", "#63D9E8", "ombre"),
    ("Горошек", "Узоры", "#F8E7ED", "#D94E83", "dots"),
    ("Чёрно-белая геометрия", "Узоры", "#F8F7F5", "#222222", "stripes"),
    ("Шахматка", "Узоры", "#FFFFFF", "#222222", "checker"),
    ("Зебра", "Узоры", "#F8F5F0", "#252525", "zebra"),
    ("Леопард", "Узоры", "#D7A76C", "#5A3320", "leopard"),
    ("Цветочки", "Цветочный", "#FBE6EE", "#D94F86", "flowers"),
    ("Сакура", "Цветочный", "#F7F0F0", "#EBA8C1", "sakura"),
    ("Сердечки", "Романтика", "#FFE8EF", "#E62D63", "hearts"),
    ("Вишенки", "Романтика", "#FFF0E6", "#C51E3A", "cherries"),
    ("Лавандовый минимализм", "Минимализм", "#D9C9F2", "#7655A6", "minimal"),
    ("Оливковый минимализм", "Минимализм", "#C6CBA2", "#515D38", "minimal"),
    ("Мрамор", "Арт", "#F5F2EF", "#8D9AA6", "marble"),
    ("Абстракция", "Арт", "#F6C9B7", "#6D4C9A", "abstract"),
    ("Глиттер розовый", "Блёстки", "#B92F70", "#FFD4F0", "glitter"),
    ("Глиттер золотой", "Блёстки", "#8A5C12", "#FFE49A", "glitter"),
    ("Глиттер ледяной", "Блёстки", "#A7C9DD", "#FFFFFF", "glitter"),
    ("Ночной космос", "Арт", "#11152E", "#9B8CFF", "galaxy"),
    ("Деним", "Узоры", "#244E86", "#9EC9F3", "denim"),
]

CATEGORIES = ["Все стили"] + list(dict.fromkeys(d[1] for d in DESIGNS))

def rgb(hex_color):
    h = hex_color.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def blend(a, b, t):
    return tuple(int(a[i] * (1-t) + b[i] * t) for i in range(3))

def make_pattern(size, design, seed=7):
    name, category, base_hex, accent_hex, kind = design
    w, h = size
    base, accent = rgb(base_hex), rgb(accent_hex)
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    # Нежный вертикальный градиент как основа покрытия
    for y in range(h):
        t = y / max(1, h-1)
        col = blend(base, accent, t * 0.22)
        arr[y, :, :] = col
    im = Image.fromarray(arr, "RGB")
    d = ImageDraw.Draw(im, "RGBA")
    rng = random.Random(seed)
    scale = max(1, min(w, h) / 100)
    if kind == "plain":
        # Глянцевый блик
        d.ellipse((w*.22, -h*.1, w*.55, h*.7), fill=(255,255,255,28))
    elif kind == "french":
        d.rectangle((0, h*.77, w, h), fill=(*accent, 245))
        d.ellipse((-w*.15, h*.62, w*1.15, h*.92), fill=(*accent, 255))
        d.rectangle((0, h*.82, w, h), fill=(*accent, 255))
    elif kind == "ombre":
        for y in range(h):
            t = y / max(1, h-1)
            col = blend(base, accent, t)
            d.line((0,y,w,y), fill=(*col,255))
    elif kind in ("chrome", "pearl", "cat_eye"):
        for x in range(w):
            t = x / max(1,w-1)
            col = blend(base, accent, abs(math.sin(t*math.pi*2)) * .75)
            d.line((x,0,x,h), fill=(*col,255))
        d.line((w*.22,0,w*.42,h), fill=(255,255,255,80), width=max(2,int(scale*5)))
        if kind == "cat_eye":
            d.ellipse((w*.2,h*.25,w*.8,h*.62), outline=(255,255,255,120), width=max(2,int(scale*3)))
    elif kind in ("dots", "glitter"):
        count = 100 if kind == "glitter" else 22
        for _ in range(count):
            x, y = rng.randrange(w), rng.randrange(h)
            r = rng.uniform(1, 3) * scale
            color = (255,255,255,190) if rng.random() > .35 else (*accent,210)
            d.ellipse((x-r,y-r,x+r,y+r), fill=color)
    elif kind == "stripes":
        step = max(8, int(16*scale))
        for x in range(-h, w+h, step):
            d.line((x,0,x+h,h), fill=(*accent,190), width=max(2,int(scale*4)))
    elif kind == "checker":
        step = max(8, int(15*scale))
        for y in range(0,h,step):
            for x in range(0,w,step):
                if (x//step+y//step)%2 == 0: d.rectangle((x,y,x+step,y+step), fill=(*accent,230))
    elif kind == "zebra":
        for y in range(-h//4,h+h//4,max(9,int(18*scale))):
            pts=[]
            for x in range(0,w+1,max(4,int(6*scale))): pts.append((x, y+math.sin(x/max(1,w)*math.pi*4)*h*.04))
            if len(pts)>1: d.line(pts, fill=(*accent,230), width=max(2,int(scale*4)))
    elif kind == "leopard":
        for _ in range(18):
            x,y=rng.randrange(w),rng.randrange(h); rx=rng.uniform(3,7)*scale; ry=rng.uniform(2,5)*scale
            d.ellipse((x-rx,y-ry,x+rx,y+ry), fill=(*accent,210))
            d.arc((x-rx*1.5,y-ry*1.5,x+rx*1.5,y+ry*1.5), 15, 300, fill=(30,20,10,230), width=max(1,int(scale*2)))
    elif kind in ("flowers", "sakura"):
        for _ in range(7):
            x,y=rng.randrange(w),rng.randrange(h); r=5*scale
            for a in range(5):
                ang=a*2*math.pi/5
                px=x+math.cos(ang)*r; py=y+math.sin(ang)*r
                d.ellipse((px-r*.55,py-r*.55,px+r*.55,py+r*.55), fill=(*accent,210))
            d.ellipse((x-r*.3,y-r*.3,x+r*.3,y+r*.3), fill=(255,218,90,240))
    elif kind == "hearts":
        for _ in range(7):
            x,y=rng.randrange(w),rng.randrange(h); r=5*scale
            d.ellipse((x-r,y-r,x,y+r*.2), fill=(*accent,230)); d.ellipse((x,y-r,x+r,y+r*.2), fill=(*accent,230))
            d.polygon([(x-r,y),(x+r,y),(x,y+r*1.5)], fill=(*accent,230))
    elif kind == "cherries":
        for _ in range(5):
            x,y=rng.randrange(w),rng.randrange(h); r=4*scale
            d.line((x,y,x+r*2,y-r*3), fill=(50,110,55,240), width=max(1,int(scale*2)))
            d.ellipse((x-r,y-r,x+r,y+r), fill=(*accent,245)); d.ellipse((x+r,y-r*1.2,x+3*r,y+r*.8), fill=(*accent,245))
    elif kind == "minimal":
        d.line((w*.2,h*.2,w*.8,h*.8), fill=(*accent,230), width=max(2,int(scale*2)))
        d.ellipse((w*.35,h*.35,w*.65,h*.65), outline=(*accent,220), width=max(2,int(scale*2)))
    elif kind == "marble":
        for _ in range(9):
            pts=[]
            x0=rng.randrange(w); y0=rng.randrange(h)
            for i in range(7): pts.append((x0+i*w/6, y0+math.sin(i*1.5+rng.random())*h*.07))
            d.line(pts, fill=(*accent,110), width=max(1,int(scale*2)))
    elif kind == "abstract":
        for _ in range(8):
            x,y=rng.randrange(w),rng.randrange(h); r=rng.uniform(5,15)*scale
            d.arc((x-r,y-r,x+r,y+r),rng.randrange(360),rng.randrange(360),fill=(*accent,210),width=max(2,int(scale*3)))
    elif kind == "galaxy":
        for _ in range(100):
            x,y=rng.randrange(w),rng.randrange(h); r=rng.choice([1,1,2])*scale
            d.ellipse((x-r,y-r,x+r,y+r), fill=(255,255,255,rng.randrange(100,255)))
        d.ellipse((w*.15,h*.3,w*.85,h*.7), fill=(*accent,40))
    elif kind == "denim":
        for x in range(0,w,max(3,int(5*scale))): d.line((x,0,x,h), fill=(220,240,255,45), width=1)
        for y in range(0,h,max(3,int(5*scale))): d.line((0,y,w,y), fill=(220,240,255,45), width=1)
    return im

st.title("💅 AI Nail Stylist")
st.caption("Большая коллекция дизайнов и примерка на фотографии ногтей")
st.info("Для аккуратной примерки отметьте зелёной кистью поверхность каждого ногтя. Сейчас приложение накладывает выбранный дизайн на отмеченные области; автоматическое распознавание ногтей — следующий этап.")

with st.sidebar:
    st.header("1. Фото ногтей")
    source = st.radio("Источник фото", ["Камера", "Загрузить фото"], horizontal=True)
    uploaded = st.camera_input("Сфотографировать ногти") if source == "Камера" else st.file_uploader("Выберите фото", type=["jpg","jpeg","png","webp"])
    st.header("2. Каталог")
    category = st.selectbox("Категория дизайна", CATEGORIES)
    search = st.text_input("Найти дизайн", placeholder="Например, френч или хром")
    st.header("3. Настройка примерки")
    brush = st.slider("Размер кисти для отметки ногтей", 8, 50, 25)
    opacity = st.slider("Интенсивность покрытия", 30, 100, 82) / 100

visible = [d for d in DESIGNS if (category == "Все стили" or d[1] == category) and search.lower() in d[0].lower()]
if not visible:
    st.warning("По запросу ничего не найдено. Попробуйте другое название или выберите «Все стили».")
else:
    chosen_name = st.selectbox("Выберите дизайн", [d[0] for d in visible])
    chosen = next(d for d in visible if d[0] == chosen_name)
    a,b,c = st.columns([1,1,2])
    a.metric("Дизайнов в каталоге", len(DESIGNS))
    b.metric("Категорий", len(CATEGORIES)-1)
    c.markdown(f"**Выбранный дизайн:** {chosen[0]}  \nКатегория: {chosen[1]}")

    if uploaded is not None:
        original = Image.open(uploaded).convert("RGB")
        original.thumbnail((900, 1200))
        display = original.copy()
        display.thumbnail((680, 900))
        cw,ch = display.size
        st.subheader("Отметьте ногти для примерки")
        st.write("Проведите пальцем по поверхности каждого ногтя зелёной кистью. Старайтесь не выходить за края ногтевой пластины.")
        canvas_result = st_canvas(
            fill_color="rgba(0, 255, 0, 0.0)", stroke_width=brush, stroke_color="#00FF00",
            background_image=display, update_streamlit=True, height=ch, width=cw,
            drawing_mode="freedraw", display_toolbar=True, key="nail_canvas"
        )
        if st.button("✨ Примерить выбранный дизайн", type="primary", use_container_width=True):
            if canvas_result.image_data is None:
                st.error("Сначала отметьте ногти зелёной кистью.")
            else:
                canvas = np.array(canvas_result.image_data).astype(np.uint8)
                # Находим именно ярко-зелёные мазки, не используя цвет кожи/ногтей как ориентир.
                mark = ((canvas[:,:,1] > 125) & (canvas[:,:,1] > canvas[:,:,0]*1.35) & (canvas[:,:,1] > canvas[:,:,2]*1.25)).astype(np.uint8)*255
                mask = Image.fromarray(mark, "L").resize(original.size, Image.Resampling.BILINEAR)
                mask = mask.filter(ImageFilter.GaussianBlur(radius=1.2))
                if np.array(mask).max() < 15 or np.count_nonzero(np.array(mask)>30) < 40:
                    st.error("Не удалось найти зелёные отметки. Нарисуйте по ногтям ещё раз зелёной кистью.")
                else:
                    pattern = make_pattern(original.size, chosen, seed=DESIGNS.index(chosen)+11)
                    # Смешиваем фактуру с оригинальной фотографией, сохраняя видимость формы и света.
                    toned = Image.blend(original, pattern, opacity)
                    result = Image.composite(toned, original, mask)
                    st.session_state["nail_result"] = result
                    st.session_state["nail_result_name"] = chosen[0]
        if "nail_result" in st.session_state:
            st.subheader("Результат примерки")
            st.image(st.session_state["nail_result"], caption=st.session_state.get("nail_result_name", "Дизайн"), use_container_width=True)
            buf = io.BytesIO(); st.session_state["nail_result"].save(buf, format="PNG")
            st.download_button("⬇️ Сохранить результат", data=buf.getvalue(), file_name="ai_nail_stylist_tryon.png", mime="image/png", use_container_width=True)
    else:
        st.subheader("Вдохновение: каталог дизайнов")
        st.write("Выберите категорию слева, чтобы просмотреть идеи. Загрузите фото или откройте камеру, чтобы примерить дизайн на своих ногтях.")
        cols = st.columns(3)
        for i, design in enumerate(visible[:18]):
            swatch = make_pattern((220, 280), design, seed=i+4)
            with cols[i%3]:
                st.image(swatch, use_container_width=True)
                st.markdown(f"**{design[0]}**  \n<small>{design[1]}</small>", unsafe_allow_html=True)

with st.expander("Что умеет эта версия"):
    st.markdown("""
- Камера телефона или загрузка готовой фотографии.
- Каталог из 36 дизайнов в 10+ категориях.
- Френч, градиенты, хром, кошачий глаз, блёстки, цветочные мотивы, геометрия и другие стили.
- Ручная отметка ногтевых пластин и наложение дизайна только на отмеченные области.
- Сохранение результата в PNG.
