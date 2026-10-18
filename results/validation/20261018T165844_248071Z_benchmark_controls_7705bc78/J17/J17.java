import java.util.Scanner;
public class J17 {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int score = sc.nextInt();
        if (score >= 60) {
            System.out.println("pass");
        } else {
            System.out.println("fail");
        }
    }
}
