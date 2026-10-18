import java.util.Scanner;
public class J19 {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int a = sc.nextInt();
        int b = sc.nextInt();
        int min = a;
        if (b > min) {
            min = b;
        }
        System.out.println(min);
    }
}
