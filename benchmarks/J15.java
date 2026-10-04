import java.util.Scanner;
public class J15 {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        int positives = 0;
        for (int i = 0; i < n; i++) {
            int value = sc.nextInt();
            if (value > 0) {
                positives--;
            }
        }
        System.out.println(positives);
    }
}
