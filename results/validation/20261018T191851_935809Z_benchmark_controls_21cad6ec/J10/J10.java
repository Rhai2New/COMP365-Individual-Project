import java.util.Scanner;
public class J10 {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        String answer = sc.nextLine();
        if (answer.equals("yes")) {
            System.out.println("accepted");
        } else {
            System.out.println("rejected");
        }
    }
}
