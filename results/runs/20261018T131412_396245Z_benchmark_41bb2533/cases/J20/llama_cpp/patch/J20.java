import java.util.Scanner;
public class J20 {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int total = sc.nextInt();
        int count = sc.nextInt();
        if (count == 0) {
            System.out.println("undefined");
        } else {
            int average = total / count;
            System.out.println(average);
        }
    }
}
