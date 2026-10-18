import java.util.Scanner;
public class J07 {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int a = sc.nextInt();
        int b = sc.nextInt();
        int max = a;
        if (b < a) {
            max = b;
        }
        System.out.println(max);
    }
}
