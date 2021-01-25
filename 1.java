class Main {
    public static int calc(int a, int b) {
        int ans = 1, t = 0;
        String s = "";
        for (int i = a; i <= b; i++) {
            ans *= i;
            s += (char)('a' + t);
        }
        ans += s.length() + (int)s.charAt(0);
        return ans;
    }
}