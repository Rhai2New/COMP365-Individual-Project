import java.util.Scanner;
public class J13 {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        int max = 0;
        for (int i = 0; i < n; i++) {
            int value = sc.nextInt();
            if (value > max) {
                max = value;
            }
        }
        System.out.println(max);
    }
}
