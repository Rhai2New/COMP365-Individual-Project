import java.util.Scanner;
public class J16 {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        int product = 1;
        for (int i = 0; i < n; i++) {
            int value = sc.nextInt();
            product *= value;
        }
        System.out.println(product);
    }
}
