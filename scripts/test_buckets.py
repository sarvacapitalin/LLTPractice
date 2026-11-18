import re
from scripts.test_pdf_parse import parse_cmap, get_obj_stream, decode_stream, get_page_contents

def test_buckets():
    with open("general-driving-principles-english.pdf", "rb") as f:
        pdf = f.read()
    cmap = parse_cmap(get_obj_stream(pdf, 128))
    pages = get_page_contents(pdf)
    
    # Test on Page 2 (Contents 15)
    stream = get_obj_stream(pdf, pages[1][1])
    elems = decode_stream(stream, cmap)
    
    print("Page 2 raw elements with x coords:")
    for x, y, t in elems[:25]:
        print(f"x={x:6.2f}: {repr(t)}")

if __name__ == "__main__":
    test_buckets()
