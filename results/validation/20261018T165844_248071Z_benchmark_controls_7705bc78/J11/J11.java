import java.util.Scanner;
public class J11 {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int age = sc.nextInt();
        if (age < 0 || age > 120) {
            System.out.println("invalid");
        } else {
            System.out.println("valid");
        }
    }
}
