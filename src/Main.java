
import java.util.Arrays;
public class quick
{
    public static void main(String[] args)
    {
        int arr[]={5,4,3,2,1};
        Sort(arr,0,arr.length-1);
        System.out.println(Arrays.toString(arr);
    }
    static void Sort(int arr[],int low,int h)
    {
        if(low>=h)
        {
            return;
        }
        int s=low;
        int e=h;
        int m=s+(e-s)/2;
        int p=arr[m];
        while(s<=e)
        {
            while(arr[s]<p)
            {
                s++;
            }
            while(arr[e]>p)
            {
                e--;
            }
            if(s<=e)
            {
                int temp=arr[s];
                arr[s]=arr[e];
                arr[e]=temp;
                s++;
                e--;
            }
        }
        Sort(arr,low,e);
        Sort(arr,s,h);
    }
}