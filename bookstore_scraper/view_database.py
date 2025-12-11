import sqlite3
from tabulate import tabulate

def view_books(db_path='books.db'):
    conn = sqlite3.connect('books.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM books ORDER BY scraped_at DESC LIMIT 20')
    rows = cursor.fetchall()
    
    headers = ['ID', 'URL', 'Title', 'Price', 'Rating', 'Availability', 'Scraped']
    print(tabulate(rows, headers=headers, tablefmt='grid', maxcolwidths=[5, 30, 40, 8, 8, 15, 20, 20]))
    
    # Stats
    cursor.execute('SELECT COUNT(*), AVG(price), MIN(price), MAX(price) FROM books WHERE price IS NOT NULL')
    stats = cursor.fetchone()
    print(f"\n📊 Total Books: {stats[0]}")
    if stats[1]:
        print(f"💰 Average Price: £{stats[1]:.2f}")
        print(f"📉 Min Price: £{stats[2]:.2f}")
        print(f"📈 Max Price: £{stats[3]:.2f}")
    
    connection.close()
if __name__ == '__main__':
    view_books()