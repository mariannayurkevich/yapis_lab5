using System;
using System.Drawing;
using System.IO;

public static class Runtime {
    public static Bitmap LoadImage(string path) { 
        if (File.Exists(path)) {
            using (var temp = new Bitmap(path)) { return new Bitmap(temp); }
        } else {
            return new Bitmap(100, 100); 
        }
    }
    
    public static void SaveImage(Bitmap bmp, string path) { 
        if (bmp == null) return;
        try { bmp.Save(path); } catch {}
    }
    
    public static Bitmap CreateImage(int w, int h) { return new Bitmap(w, h); }
    
    public static int GetWidth(Bitmap bmp) { return (bmp == null) ? 0 : bmp.Width; }
    public static int GetHeight(Bitmap bmp) { return (bmp == null) ? 0 : bmp.Height; }
    
    public static Color ToColor(int r, int g, int b) { return Color.FromArgb(255, r, g, b); }
    public static Color GetPixel(Bitmap bmp, int x, int y) { return bmp.GetPixel(x, y); }
    public static void SetPixel(Bitmap bmp, int x, int y, Color c) { bmp.SetPixel(x, y, c); }
    
    public static int Clamp(int val, int min, int max) {
        if (val < min) return min;
        if (val > max) return max;
        return val;
    }
    
    public static int ReadInt() {
        try {
            string line = Console.ReadLine();
            return int.Parse(line);
        } catch {
            Console.WriteLine("Invalid number, defaulting to 0");
            return 0;
        }
    }

    public static double ReadFloat() {
    try {
        string line = Console.ReadLine();
        return double.Parse(line, System.Globalization.CultureInfo.InvariantCulture);
    } catch {
        Console.WriteLine("Invalid float number, defaulting to 0.0");
        return 0.0;
    }
    }

    public static void Write(string val) { Console.Write(val); }
    public static void Write(int val) { Console.Write(val); }
    public static void Write(double val) { Console.Write(val); }
    public static void Write(bool val) { Console.Write(val); }
    public static void Write(object val) { Console.Write(val); }
}